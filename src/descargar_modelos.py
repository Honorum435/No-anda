"""Descarga por adelantado TODOS los modelos de IA que usa el asistente, para que la
primera consulta (o el primer dictado) no se quede esperando. Se corre en la instalacion.

Cada bloque va aparte: si uno falla (por ejemplo, se corta internet a mitad), los demas
igual quedan descargados y el instalador puede seguir.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from comun import MODELO_EMBEDDINGS, MODELO_NER, MODELO_RERANK
from transcribir import MODELO_WHISPER

fallos = []


def bajar(descripcion, funcion):
    print(f"-> {descripcion} ...", flush=True)
    try:
        funcion()
        print("   listo.")
    except Exception as e:
        fallos.append(descripcion)
        print(f"   /!\\ no se pudo: {type(e).__name__}. Se baja solo la primera vez que se use.")


def _embeddings():
    from sentence_transformers import SentenceTransformer
    SentenceTransformer(MODELO_EMBEDDINGS)


def _ner():
    from transformers import pipeline
    pipeline("token-classification", model=MODELO_NER, aggregation_strategy="simple")


def _rerank():
    from sentence_transformers import CrossEncoder
    CrossEncoder(MODELO_RERANK)


def _whisper():
    from faster_whisper import WhisperModel
    WhisperModel(MODELO_WHISPER, device="cpu", compute_type="int8")


bajar(f"Busqueda por significado ({MODELO_EMBEDDINGS})", _embeddings)
bajar(f"Anonimizacion de datos personales ({MODELO_NER})", _ner)
bajar(f"Reordenado de resultados ({MODELO_RERANK})", _rerank)
bajar(f"Dictado por voz (whisper {MODELO_WHISPER})", _whisper)

print()
if fallos:
    print("Quedaron pendientes: " + ", ".join(fallos))
else:
    print("Modelos listos.")
