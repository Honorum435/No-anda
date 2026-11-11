"""Llamada a Gemini tolerante a los picos de demanda de la capa gratis.

Google devuelve 503 UNAVAILABLE ("high demand") o 429 RESOURCE_EXHAUSTED de forma
intermitente. Son transitorios: reintentar con una espera creciente resuelve la mayoria.
Si aun asi no responde, se prueban los modelos de respaldo de comun.MODELOS_RESPALDO.
"""
import random
import time

from comun import MODELO_GEMINI, MODELOS_RESPALDO

# Codigos HTTP que conviene reintentar (el resto son errores nuestros: clave mala,
# prompt invalido, etc., y reintentar no cambiaria nada).
CODIGOS_TRANSITORIOS = {429, 500, 502, 503, 504}
TEXTOS_TRANSITORIOS = ("unavailable", "resource_exhausted", "high demand",
                       "overloaded", "try again later", "deadline")


def es_transitorio(e):
    codigo = getattr(e, "code", None) or getattr(e, "status_code", None)
    if isinstance(codigo, int) and codigo in CODIGOS_TRANSITORIOS:
        return True
    msg = str(e).lower()
    if any(str(c) in msg for c in CODIGOS_TRANSITORIOS):
        return True
    return any(t in msg for t in TEXTOS_TRANSITORIOS)


def generar(contents, api_key, modelo=None, intentos=4, espera_base=2.0, log=None):
    """Pide texto a Gemini. Devuelve (texto, modelo_usado).

    Reintenta 'intentos' veces el modelo principal con espera exponencial y jitter;
    agotado eso, prueba una vez cada modelo de respaldo. Si nada responde, propaga
    el ultimo error para que la interfaz lo muestre.
    """
    from google import genai

    log = log or (lambda m: None)
    cliente = genai.Client(api_key=api_key)
    candidatos = [(modelo or MODELO_GEMINI, intentos)] + [(m, 1) for m in MODELOS_RESPALDO]
    ultimo = None

    for nombre, veces in candidatos:
        for intento in range(veces):
            try:
                resp = cliente.models.generate_content(model=nombre, contents=contents)
                if resp.text:
                    return resp.text, nombre
                ultimo = RuntimeError("Gemini devolvio una respuesta vacia.")
            except Exception as e:
                ultimo = e
                if not es_transitorio(e):
                    raise
            if intento < veces - 1:
                espera = espera_base * (2 ** intento) + random.uniform(0, 1)
                log(f"Gemini saturado ({nombre}); reintento en {espera:.0f}s…")
                time.sleep(espera)
        if len(candidatos) > 1:
            log(f"Probando modelo de respaldo tras fallar {nombre}…")

    raise ultimo
