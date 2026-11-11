"""Genera una ficha-resumen de UNA causa a partir de extractos de sus documentos.

Privacidad: el NOMBRE de la causa (suele ser el apellido del cliente) NO se envia a la nube.
Los extractos se anonimizan antes de mandarse a Gemini y se restauran localmente.

La ficha trae una linea de tiempo en tabla: cada hito cita el [Extracto N] del que sale,
para poder abrir el documento original y verificarlo (en derecho, una fecha sin fuente
no sirve).
"""
import os

from comun import MODELO_NER
from causas import fragmentos_de_caso, documentos_de_caso

PROMPT = """Sos un asistente para un abogado penalista argentino.
A partir de EXTRACTOS de los documentos de UNA causa del estudio, arma una FICHA RESUMEN clara y util.

Reglas:
- Usa SOLO lo que aparece en los extractos. Si un dato no surge, escribi "No surge del archivo".
- NO inventes nombres, fechas, delitos, caratulas ni jurisprudencia. NO deduzcas fechas.
- Algunos datos pueden venir como [PERSONA_1], [DNI_1], [DOMICILIO_1]. Dejalos TAL CUAL.
- Cuando algo sale de un extracto, citalo como [Extracto N].

Devolve la ficha en este formato (markdown):

### Datos de la causa
- **Caratula:** ...
- **Tribunal / Juzgado:** ...
- **Fiscalia / Querella:** ...
- **Imputado/s:** ...
- **Delito/s:** ...
- **Estado procesal:** ...

### Linea de tiempo
| Fecha | Que paso | Fuente |
|---|---|---|
| dd/mm/aaaa | hito en una linea | [Extracto N] |
(una fila por hito, de la mas vieja a la mas nueva; si el documento no dice la fecha,
escribi "Sin fecha en el documento" y ponela al final; si no hay hitos, una sola fila
que diga "No surge del archivo")

### Resumen de los hechos
(2 a 5 oraciones, citando [Extracto N])

### Escritos / piezas detectadas
(que tipos de escritos aparecen en los extractos)

### Puntos de atencion
(plazos, pendientes o riesgos mencionados; si no hay nada, omiti esta seccion)

EXTRACTOS DE LA CAUSA:
{contexto}

FICHA:"""


def generar_ficha(caso, api_key=None, log=None):
    """Devuelve (texto, documentos, meta). texto=None si falta la clave de Gemini.
    meta['extractos'] dice de que documento sale cada [Extracto N].
    La anonimizacion es obligatoria (ver preguntar.generar_respuesta)."""
    api_key = api_key or os.environ.get("GEMINI_API_KEY")
    docs = documentos_de_caso(caso)
    frags = fragmentos_de_caso(caso)
    if not api_key:
        return None, docs, {"anonimizado": False, "ocultos": 0}
    if not frags:
        return "No encontre documentos de esa causa en el indice.", docs, {
            "anonimizado": False, "ocultos": 0}

    aviso = log or (lambda m: None)
    aviso(f"Leyendo {len(docs)} documento(s) de la causa…")
    aviso("Ocultando datos personales antes de salir a la nube…")
    from anonimizar import anonimizar_varios, restaurar
    from causas import nombres_de_clientes, nombres_de_la_causa
    # El apellido de ESTA causa se tapa siempre, aunque tambien se use como palabra comun.
    extra = sorted(set(nombres_de_clientes()) | set(nombres_de_la_causa(caso)))
    textos_env, mapa = anonimizar_varios([f["texto"] for f in frags], MODELO_NER, extra)

    contexto = "\n\n".join(f"[Extracto {i + 1}]\n{t}" for i, t in enumerate(textos_env))
    prompt = PROMPT.format(contexto=contexto)
    aviso("Armando la ficha…")
    from nube import generar
    texto, modelo = generar(prompt, api_key, log=log)
    texto = restaurar(texto, mapa)
    extractos = [{"nombre": f.get("nombre"), "ruta": f.get("ruta"),
                  "texto": (f.get("texto") or "")[:300]} for f in frags]
    return texto, docs, {"anonimizado": True, "ocultos": len(mapa), "modelo": modelo,
                         "extractos": extractos}
