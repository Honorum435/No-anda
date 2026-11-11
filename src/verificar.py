"""Chequeo de instalacion: dice que anda y que falta, en castellano y sin tecnicismos.

Lo corre el instalador al final. Sale con codigo 0 si todo lo IMPRESCINDIBLE esta,
y 1 si falta algo sin lo cual el asistente no arranca.
"""
import os
import shutil
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

OK, AVISO, ERROR = "  [OK]  ", "  [!]   ", "  [X]   "
problemas, avisos = [], []


def probar(descripcion, funcion, critico=True):
    try:
        detalle = funcion()
    except Exception as e:
        detalle = f"{type(e).__name__}: {e}"
        if critico:
            problemas.append(descripcion)
            print(ERROR + f"{descripcion}: {detalle}")
        else:
            avisos.append(descripcion)
            print(AVISO + f"{descripcion}: {detalle}")
        return False
    print(OK + f"{descripcion}" + (f" — {detalle}" if detalle else ""))
    return True


def _librerias():
    import numpy, streamlit, sentence_transformers, docx, pypdf  # noqa: F401
    from google import genai  # noqa: F401
    return "todas las librerias basicas"


def _exportacion():
    import reportlab  # noqa: F401
    from docx import Document  # noqa: F401
    return "Word y PDF"


def _modelo():
    from comun import MODELO_EMBEDDINGS
    from sentence_transformers import SentenceTransformer
    m = SentenceTransformer(MODELO_EMBEDDINGS)
    v = m.encode(["query: prueba"], normalize_embeddings=True)
    return f"{MODELO_EMBEDDINGS} ({v.shape[1]} dimensiones)"


def _gpu():
    import torch
    if torch.cuda.is_available():
        return torch.cuda.get_device_name(0)
    raise RuntimeError("sin placa compatible; el indexado va a usar el procesador (mas lento)")


def _indice():
    from comun import CARPETA_INDICE
    import json
    fp = CARPETA_INDICE / "fragmentos.json"
    if not fp.exists():
        raise RuntimeError("todavia no hay archivo indexado (usa la pestana 'Archivo')")
    frags = json.loads(fp.read_text(encoding="utf-8"))
    docs = len({f.get("ruta") for f in frags})
    return f"{docs} documentos / {len(frags)} fragmentos"


def _tesseract():
    exe = shutil.which("tesseract") or next(
        (c for c in [r"C:\Program Files\Tesseract-OCR\tesseract.exe",
                     r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe"]
         if Path(c).exists()), None)
    if not exe:
        raise RuntimeError("no instalado; no se van a poder leer los PDF escaneados")
    from comun import BASE
    idioma = (BASE / "datos" / "tessdata" / "spa.traineddata").exists()
    return exe + ("" if idioma else "  (ojo: falta el idioma espanol)")


def _word():
    import pythoncom
    import win32com.client as win32
    pythoncom.CoInitialize()
    w = win32.Dispatch("Word.Application")
    v = w.Version
    w.Quit()
    return f"version {v}"


def _clave():
    from comun import BASE
    archivo = BASE / "datos" / ".clave_gemini"
    if os.environ.get("GEMINI_API_KEY") or (archivo.exists() and archivo.read_text().strip()):
        return "cargada"
    raise RuntimeError("todavia no esta; se carga desde el boton de Configuracion de la app")


print("\nImprescindible para que el asistente abra:")
probar("Librerias de Python", _librerias)
probar("Exportar a Word y PDF", _exportacion)
probar("Modelo de busqueda (local)", _modelo)

print("\nOpcional (el asistente anda igual, con menos funciones):")
probar("Placa de video", _gpu, critico=False)
probar("Archivo indexado", _indice, critico=False)
probar("Tesseract / OCR", _tesseract, critico=False)
probar("Microsoft Word (.doc viejos)", _word, critico=False)
probar("Clave de Gemini", _clave, critico=False)

print()
if problemas:
    print(f"Faltan {len(problemas)} cosa(s) imprescindible(s): " + ", ".join(problemas))
    sys.exit(1)
if avisos:
    print("Todo lo imprescindible esta. Pendientes opcionales: " + ", ".join(avisos))
else:
    print("Todo en orden.")
sys.exit(0)
