"""Checklist orientativa de completitud de un escrito penal (100% local, sin nube).

Chequea por palabras clave si el borrador contiene las partes tipicas del tipo de escrito
y lista los marcadores [COMPLETAR: ...] que quedaron pendientes. No es un control juridico:
es una ayuda para no olvidarse secciones.
"""
import re
import unicodedata


def _norm(t):
    """minusculas y sin acentos, para comparar de forma robusta."""
    t = unicodedata.normalize("NFKD", t or "")
    return "".join(c for c in t if not unicodedata.combining(c)).lower()


# Partes comunes a la mayoria de los escritos
_BASE = [
    ("Encabezado / objeto", ["objeto", "interpone", "promuevo", "promueve", "vengo a", "me presento", "sumario"]),
    ("Hechos / antecedentes", ["hecho", "antecedent", "resulta", "surge de"]),
    ("Fundamentos de derecho", ["derecho", "fundament", "articulo", "art.", "codigo", "garantia", "jurisprudenc"]),
    ("Ofrecimiento de prueba", ["prueba", "ofrec", "documental", "testimonial", "pericial"]),
    ("Petitorio", ["petitorio", "por todo ello", "solicito", "pido", "se sirva"]),
]

_RESERVA = ("Reserva del caso federal", ["caso federal", "cuestion federal", "reserva"])

_ESPECIFICAS = {
    "excarcelación / eximición": [
        ("Procedencia y norma (arts. 316/317 CPPN o local)", ["excarcel", "eximicion", "316", "317", "210", "221"]),
        ("Arraigo (domicilio, trabajo, familia)", ["arraigo", "domicilio", "trabajo", "familia"]),
        ("Ausencia de peligros procesales (fuga/entorpecimiento)", ["peligro de fuga", "entorpecimiento", "riesgo procesal", "elud", "fuga"]),
    ],
    "nulidad": [
        ("Acto viciado identificado", ["nulidad", "acto", "vicio", "irregular", "defecto"]),
        ("Perjuicio concreto", ["perjuicio", "agravio", "interes"]),
        ("Garantía / norma violada", ["debido proceso", "defensa en juicio", "garantia", "articulo"]),
        _RESERVA,
    ],
    "recurso (casación/apelación)": [
        ("Admisibilidad / interposición en término", ["admisibilidad", "en termino", "plazo", "tempestiv", "tiempo y forma"]),
        ("Autosuficiencia del recurso", ["autosuficien"]),
        ("Agravios", ["agravio"]),
        ("Motivos (inobservancia / errónea aplicación / arbitrariedad)", ["inobservancia", "erronea", "arbitrar", "motivo", "fundamentacion"]),
        _RESERVA,
    ],
    "sobreseimiento": [
        ("Causal de sobreseimiento (art. 336 CPPN o local)", ["sobreseimiento", "336", "atipic", "no fue autor", "extincion"]),
        ("Fundamentación de la causal", ["toda vez", "en virtud", "por cuanto", "fundament"]),
    ],
}

# Mapea el texto libre del 'tipo' a una plantilla especifica
_ALIAS = [
    (["excarcel", "eximicion", "exencion de prision", "morigerac", "arresto domiciliario", "cese de prision"], "excarcelación / eximición"),
    (["nulidad", "nulo"], "nulidad"),
    (["casacion", "apelacion", "recurso", "queja", "impugnacion", "inconstitucional"], "recurso (casación/apelación)"),
    (["sobreseimiento"], "sobreseimiento"),
]


def _plantilla(tipo):
    n = _norm(tipo)
    for claves, nombre in _ALIAS:
        if any(c in n for c in claves):
            return _ESPECIFICAS[nombre], nombre
    return [], ""


def evaluar(texto, tipo=""):
    """Devuelve dict: partes [(nombre, presente)], faltan_completar [str],
    cobertura (0..1) y categoria (str)."""
    n = _norm(texto)
    especificas, categoria = _plantilla(tipo)
    partes = []
    for nombre, claves in _BASE + especificas:
        presente = any(_norm(c) in n for c in claves)
        partes.append((nombre, presente))
    completar = re.findall(r"\[COMPLETAR[^\]]*\]", texto or "")
    presentes = sum(1 for _, p in partes if p)
    cobertura = presentes / len(partes) if partes else 0.0
    return {"partes": partes, "faltan_completar": completar,
            "cobertura": cobertura, "categoria": categoria}
