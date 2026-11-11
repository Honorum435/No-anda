"""Configuracion compartida por todo el proyecto (modelos y rutas)."""
import os

# Evita un crash por conflicto de OpenMP (libiomp5md.dll) al cargar torch en Windows.
os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")

from pathlib import Path

# Carpeta raiz del proyecto (la que contiene src/ y datos/)
BASE = Path(__file__).resolve().parent.parent

CARPETA_EJEMPLOS = BASE / "datos" / "ejemplos"
CARPETA_INDICE = BASE / "datos" / "indice"

# Modelo de embeddings (corre LOCAL y gratis, usa la placa si esta disponible).
# multilingual-e5-base anda muy bien en espanol.
MODELO_EMBEDDINGS = "intfloat/multilingual-e5-base"

# Modelo de Gemini para redactar la respuesta final (capa gratis para pruebas).
# Nota: en esta cuenta, gemini-2.0-flash da cuota 0; los modelos 2.5 si andan gratis.
# Si este nombre no esta disponible para tu clave, corre src/listar_modelos.py
# para ver cuales hay y cambialo aca.
MODELO_GEMINI = "gemini-2.5-flash"

# Respaldos si el principal esta saturado (503) o sin cuota. Se prueban en orden.
MODELOS_RESPALDO = ["gemini-2.5-flash-lite", "gemini-3-flash-preview"]

# Modelo de NER para detectar nombres de personas al anonimizar (corre LOCAL, gratis).
MODELO_NER = "Babelscape/wikineural-multilingual-ner"

# Modelo de reranking (cross-encoder multilingue, corre LOCAL). Reordena por relevancia.
MODELO_RERANK = "cross-encoder/mmarco-mMiniLMv2-L12-H384-v1"

# Cuantos fragmentos relevantes se usan para responder.
TOP_K = 5

# Puertos: la app de escritorio solo escucha en esta PC; la del celular, en la red
# local y siempre con PIN.
PUERTO_ESCRITORIO = 8501
PUERTO_CELULAR = 8510


def clave_ruta(ruta):
    """Forma canonica de una ruta para compararla con otra.

    En Windows 'E:\\Casos\\a.pdf' y 'e:/casos/A.pdf' son el mismo archivo. Comparar el
    texto tal cual hacia que, por una letra de disco en minuscula, se volviera a procesar
    el disco entero y se duplicara el indice.
    """
    return os.path.normcase(os.path.normpath(str(ruta))).replace("\\", "/")
