"""Anonimiza datos personales (nombres, DNI, CUIT, email, telefono, domicilio, CBU,
patente) ANTES de enviar texto a la nube, y permite restaurarlos localmente en la respuesta.

Estrategia: detectar -> reemplazar por etiquetas consistentes ([PERSONA_1], [DNI_1], ...)
-> (enviar a la nube) -> restaurar las etiquetas por los datos reales en la respuesta.

Deteccion de nombres = NER local + formato de caratula "APELLIDO, Nombre" + propagacion
(una vez detectado un nombre, se ocultan TODAS sus apariciones, incluso en mayusculas).
Es una ayuda fuerte, NO una garantia perfecta: puede pasar por alto algun dato.
"""
import re
import unicodedata

# --- Datos estructurados (alta confianza) ---
PATRONES = {
    "DOMICILIO": re.compile(
        r"(?i)\b(?:calle|av\.?|avenida|pasaje|ruta|diagonal|bv\.?|boulevard)\s+"
        r"[A-Za-zÁÉÍÓÚáéíóúñ.]+(?:\s+[A-Za-zÁÉÍÓÚáéíóúñ.]+){0,3}\s+\d{1,5}\b"
    ),
    "DNI": re.compile(r"\b\d{1,2}\.\d{3}\.\d{3}\b|\b\d{7,8}\b"),
    "CUIT": re.compile(r"\b\d{2}-\d{8}-\d\b"),
    "EMAIL": re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b"),
    "TEL": re.compile(r"\b(?:\+?54[\s-]?)?(?:0?\d{2,4})[\s-]\d{3,4}[\s-]\d{3,4}\b"),
    # Celular o fijo escrito de corrido (1155667788, +5491155667788).
    "TEL2": re.compile(r"(?<![\d/.-])\+?\d{10,13}(?![\d/-])"),
    # CBU / CVU: 22 digitos.
    "CBU": re.compile(r"(?<!\d)\d{22}(?!\d)"),
    # Patente Mercosur (AB 123 CD).
    "PATENTE": re.compile(r"\b[A-Z]{2}\s?\d{3}\s?[A-Z]{2}\b"),
}
_TIPO_REAL = {"TEL2": "TEL"}

# Datos que solo se reconocen por el contexto: el grupo 1 es lo que se oculta.
# Domicilio sin "calle" adelante ("vive en Rivadavia 5500, 3° B") y patente vieja
# ("dominio ABC 123"). Solo las palabras disparadoras ignoran mayusculas: el nombre de
# la calle tiene que empezar en mayuscula o numero, para no tapar texto comun.
PATRONES_CONTEXTO = {
    "DOMICILIO": re.compile(
        r"\b(?i:domicilio(?:\s+(?:real|legal|constituido|particular))?|domiciliad[oa]|"
        r"vive|viv[ií]a|reside|resid[ií]a|residente|sit[oa]|ubicad[oa])"
        r"\s+(?i:en\s+)?(?i:(?:la\s+)?(?:calle|av(?:enida|\.)?|pasaje)\s+)?"
        r"((?:(?:[A-ZÁÉÍÓÚÑ0-9][\wÁÉÍÓÚáéíóúñ.']*|de|del|la|las|los|y)\s+){1,5}?\d{1,5}"
        r"(?:\s*,?\s*(?:(?i:piso)\s*\d+|\d+\s*°\s*[A-Za-z]?|(?i:dto|depto)\.?\s*\w+))*)"
    ),
    "PATENTE": re.compile(r"\b(?i:dominio|patente)\s+([A-Z]{3}\s?-?\d{3})\b"),
}

# Formato tipico de caratula argentina: APELLIDO(S) en mayusculas, coma, Nombre.
# Ej: "GOMEZ, Ramon"  /  "DE LA ROSA, Juan Carlos"
PATRON_CARATULA = re.compile(
    r"\b[A-ZÁÉÍÓÚÑ]{2,}(?:\s+[A-ZÁÉÍÓÚÑ]{2,})*\s*,\s*[A-ZÁÉÍÓÚ][a-záéíóúñ]+(?:\s+[A-ZÁÉÍÓÚ][a-záéíóúñ]+)*"
)

ETIQUETAS_PERSONA = {"PER", "PERSON", "PERS"}

# Palabras que NO deben tratarse como nombre aunque aparezcan en mayusculas / junto a uno.
STOP_NOMBRES = {
    "sr", "sra", "dr", "dra", "don", "doña", "nulidad", "causa", "planteo",
    "corte", "suprema", "nacional", "constitucion", "codigo", "penal",
}

_ner = None


def _cargar_ner(modelo):
    global _ner
    if _ner is None:
        from transformers import pipeline
        _ner = pipeline("token-classification", model=modelo, aggregation_strategy="simple")
    return _ner


def _flexible(palabra):
    """Patron que encuentra la palabra con o sin tildes ni enie: si se detecto 'PEREZ' en
    la caratula, tambien tiene que taparse 'Pérez' en el cuerpo del escrito."""
    base = unicodedata.normalize("NFKD", palabra).encode("ascii", "ignore").decode().lower()
    variantes = {"a": "[aá]", "e": "[eé]", "i": "[ií]", "o": "[oó]", "u": "[uúü]", "n": "[nñ]"}
    return "".join(variantes.get(c, re.escape(c)) for c in base)


def _detectar(texto, ner, nombres_extra=()):
    """Devuelve lista de [inicio, fin, tipo, original]."""
    detecciones = []

    # 1) Datos estructurados por regex
    for tipo, patron in PATRONES.items():
        for m in patron.finditer(texto):
            detecciones.append([m.start(), m.end(), _TIPO_REAL.get(tipo, tipo), m.group()])
    for tipo, patron in PATRONES_CONTEXTO.items():
        for m in patron.finditer(texto):
            detecciones.append([m.start(1), m.end(1), tipo, m.group(1)])

    # 2) Caratula "APELLIDO, Nombre"
    for m in PATRON_CARATULA.finditer(texto):
        detecciones.append([m.start(), m.end(), "PERSONA", m.group()])

    # 3) Personas por NER
    for ent in ner(texto):
        if ent["entity_group"] in ETIQUETAS_PERSONA:
            ini, fin = ent["start"], ent["end"]
            detecciones.append([ini, fin, "PERSONA", texto[ini:fin]])

    # 4) Propagacion: tapar TODAS las apariciones de cada palabra-nombre detectada,
    #    con o sin tildes y en cualquier combinacion de mayusculas.
    palabras = set()
    for _, _, tipo, original in detecciones:
        if tipo == "PERSONA":
            for w in re.findall(r"[A-Za-zÁÉÍÓÚÑáéíóúñ]{3,}", original):
                if _flexible(w) and w.lower() not in STOP_NOMBRES:
                    palabras.add(_flexible(w))
    for patron in palabras:
        for m in re.finditer(r"\b" + patron + r"\b", texto, flags=re.IGNORECASE):
            detecciones.append([m.start(), m.end(), "PERSONA", m.group()])

    # 5) Nombres ya conocidos (los apellidos de las carpetas de causas): se tapan aunque
    #    el NER no los reconozca. Solo escritos con mayuscula, como se escribe un apellido:
    #    asi "Barrios" se oculta pero "los barrios de la ciudad" no.
    for w in nombres_extra:
        for m in re.finditer(r"\b" + _flexible(w) + r"\b", texto, flags=re.IGNORECASE):
            if m.group()[0].isupper():
                detecciones.append([m.start(), m.end(), "PERSONA", m.group()])

    return detecciones


def _aplicar(texto, detecciones, estado):
    """Reemplaza las detecciones por etiquetas consistentes, usando estado compartido."""
    detecciones.sort(key=lambda d: (d[0], -(d[1] - d[0])))
    salida, cursor = [], 0
    for ini, fin, tipo, original in detecciones:
        if ini < cursor:  # solapado con una deteccion ya aplicada
            continue
        clave = (tipo, original.strip().lower())
        token = estado["tokens"].get(clave)
        if token is None:
            estado["contadores"][tipo] = estado["contadores"].get(tipo, 0) + 1
            token = f"[{tipo}_{estado['contadores'][tipo]}]"
            estado["tokens"][clave] = token
            estado["mapa"][token] = original.strip()
        salida.append(texto[cursor:ini])
        salida.append(token)
        cursor = fin
    salida.append(texto[cursor:])
    return "".join(salida)


def anonimizar_varios(textos, modelo_ner, nombres_extra=()):
    """Anonimiza una lista de textos con un mapa compartido y consistente.
    nombres_extra: nombres conocidos que se tapan siempre (ver causas.nombres_de_clientes).
    Devuelve (lista_anonimizada, mapa) donde mapa = {etiqueta: dato_real}."""
    ner = _cargar_ner(modelo_ner)
    estado = {"mapa": {}, "tokens": {}, "contadores": {}}
    salida = [_aplicar(t, _detectar(t, ner, nombres_extra), estado) for t in textos]
    return salida, estado["mapa"]


def anonimizar(texto, modelo_ner, nombres_extra=()):
    """Anonimiza un solo texto. Devuelve (texto_anonimizado, mapa)."""
    salida, mapa = anonimizar_varios([texto], modelo_ner, nombres_extra)
    return salida[0], mapa


def restaurar(texto, mapa):
    """Reemplaza las etiquetas por los datos reales (se usa localmente, sobre la respuesta).

    Tolera que el modelo devuelva la etiqueta con otro formato ('[Persona 1]',
    '[PERSONA-1]', 'PERSONA_1'): si no, el usuario veria la etiqueta en vez del nombre.
    """
    for token in sorted(mapa, key=len, reverse=True):
        tipo, numero = token.strip("[]").rsplit("_", 1)
        variantes = (rf"\[\s*{tipo}[\s_-]*{numero}\s*\]"      # con corchetes, cualquier separador
                     rf"|\b{tipo}_{numero}\b")                 # sin corchetes, con guion bajo
        texto = re.sub(rf"(?:{variantes})(?!\d)", lambda _m, v=mapa[token]: v, texto,
                       flags=re.IGNORECASE)
    return texto


PATRON_ETIQUETA = re.compile(
    r"\[\s*(PERSONA|DNI|CUIT|EMAIL|TEL|DOMICILIO|CBU|PATENTE)[\s_-]*\d+\s*\]", re.IGNORECASE)

_A_COMPLETAR = {
    "PERSONA": "[COMPLETAR: nombre]",
    "DNI": "[COMPLETAR: DNI]",
    "CUIT": "[COMPLETAR: CUIT]",
    "EMAIL": "[COMPLETAR: email]",
    "TEL": "[COMPLETAR: telefono]",
    "DOMICILIO": "[COMPLETAR: domicilio]",
    "CBU": "[COMPLETAR: CBU]",
    "PATENTE": "[COMPLETAR: patente]",
}


def neutralizar(texto):
    """Convierte las etiquetas que quedaron sin restaurar en marcas '[COMPLETAR: ...]'.

    Se usa al redactar para un caso NUEVO: las etiquetas que sobreviven provienen de
    escritos de OTRAS causas usados como modelo. Restaurarlas metería datos de otros
    clientes en el borrador (secreto profesional), y dejarlas como [PERSONA_7] no le
    dice nada a quien lo lee.
    """
    return PATRON_ETIQUETA.sub(lambda m: _A_COMPLETAR[m.group(1).upper()], texto)
