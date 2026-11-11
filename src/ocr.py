"""OCR de PDFs escaneados (sin capa de texto) con Tesseract local (gratis, en espanol).

Renderiza cada pagina con PyMuPDF y la pasa por pytesseract (lang=spa); el texto recuperado
se AGREGA al indice con la ruta/nombre del PDF original (reusa el append incremental).

Requiere: tesseract.exe instalado + datos de idioma 'spa'. Si 'spa.traineddata' esta en
datos/tessdata, se usa de ahi via --tessdata-dir (no hace falta admin para el idioma).

Uso:
    python src/ocr.py --test 2        # prueba con 2 PDFs (no toca el indice)
    python src/ocr.py                 # OCR de todos los PDFs escaneados nuevos -> indexa
"""
import io
import json
import os
import shutil
import sys
from pathlib import Path

import numpy as np

from comun import BASE, CARPETA_INDICE, MODELO_EMBEDDINGS, clave_ruta
from extraer_texto import ruta_larga
from indexar import limpiar_texto, cortar, encode_robusto
from actualizar import _cargar_indice, leer_lista, PROC_PATH

CARPETA_DRIVE = BASE / "datos" / "drive_casos" / "MochiPato"
TESSDATA = BASE / "datos" / "tessdata"
# PDF que ya pasaron por el OCR (con o sin resultado), para no repetirlos.
OCR_PATH = CARPETA_INDICE / "ocr_hechos.json"


def pendientes_ocr(carpeta, fragmentos):
    """PDF de la carpeta que no aportaron texto y todavia no pasaron por el OCR.

    Antes se tomaban los PDF que no figuraban como 'vistos'. Pero el paso de texto, que
    corre justo antes, marca como vistos TODOS los PDF que examina, tambien los
    escaneados: el OCR no encontraba nunca nada que leer y los escaneados nuevos
    quedaban fuera del buscador para siempre.
    """
    con_texto = {clave_ruta(f.get("ruta")) for f in fragmentos if f.get("ruta")}
    hechos = {clave_ruta(r) for r in leer_lista(OCR_PATH)}
    return [p for p in Path(carpeta).rglob("*.pdf")
            if clave_ruta(p) not in con_texto and clave_ruta(p) not in hechos]

_RUTAS_TESS = [
    r"C:\Program Files\Tesseract-OCR\tesseract.exe",
    r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
    str(Path(os.environ.get("LOCALAPPDATA", "")) / "Programs" / "Tesseract-OCR" / "tesseract.exe"),
]


def config_tesseract():
    """Ubica tesseract.exe y devuelve (ok, config_idioma). config_idioma usa la carpeta
    local de datos de idioma si existe (sin admin)."""
    import pytesseract
    exe = shutil.which("tesseract") or next((c for c in _RUTAS_TESS if Path(c).exists()), None)
    if exe:
        pytesseract.pytesseract.tesseract_cmd = exe
    # Sin comillas: pytesseract parte el config por espacios y las comillas romperian la ruta.
    # (La ruta de TESSDATA no tiene espacios.)
    cfg = f"--tessdata-dir {TESSDATA}" if (TESSDATA / "spa.traineddata").exists() else ""
    return exe, cfg


def ocr_pdf(ruta, cfg="", dpi=200, max_paginas=40):
    """Devuelve el texto OCR de un PDF (hasta max_paginas)."""
    import fitz  # PyMuPDF
    import pytesseract
    from PIL import Image

    partes = []
    with fitz.open(ruta_larga(ruta)) as doc:
        for i, page in enumerate(doc):
            if i >= max_paginas:
                break
            pix = page.get_pixmap(dpi=dpi)
            img = Image.open(io.BytesIO(pix.tobytes("png")))
            partes.append(pytesseract.image_to_string(img, lang="spa", config=cfg))
    return "\n".join(partes)


def indexar_ocr(carpeta=None, test=0, dpi=200, max_paginas=40, log=None, parar=None):
    """OCR de los PDFs escaneados NUEVOS y append al indice. test>0 = solo prueba N sin indexar."""
    log = log or (lambda m: print(m, flush=True))
    exe, cfg = config_tesseract()
    if not exe:
        log("/!\\ No encontre tesseract.exe. Instala Tesseract primero (ver instrucciones).")
        return 0, 0
    log(f"tesseract: {exe}")
    log(f"idioma spa: {'carpeta local' if cfg else 'la del propio Tesseract'}")

    carpeta = Path(carpeta) if carpeta else CARPETA_DRIVE
    vectores, fragmentos = _cargar_indice()
    if vectores is None:
        log("No hay indice base. Corre primero python src/indexar.py")
        return 0, 0
    pdfs = pendientes_ocr(carpeta, fragmentos)
    if test:
        pdfs = pdfs[:test]
    log(f"PDFs escaneados a procesar: {len(pdfs)}")

    nuevos_frags, docs_ok, examinados = [], 0, []
    for n, p in enumerate(pdfs, 1):
        if parar is not None and parar():
            log(f"Cancelado por el usuario: quedan {len(pdfs) - n + 1} PDF sin procesar.")
            break
        examinados.append(str(p))
        try:
            texto = limpiar_texto(ocr_pdf(p, cfg, dpi, max_paginas))
        except Exception as e:
            log(f"  /!\\ {p.name}: {type(e).__name__}")
            continue
        trozos = [t.strip() for t in cortar(texto) if t.strip()]
        if trozos:
            docs_ok += 1
            nuevos_frags += [{"texto": t, "nombre": p.name, "ruta": str(p)} for t in trozos]
        if n % 10 == 0 or n == len(pdfs):
            log(f"  ... {n}/{len(pdfs)} (con texto: {docs_ok})")

    log(f"OCR terminado: {docs_ok} docs con texto -> {len(nuevos_frags)} fragmentos.")
    if test:
        if nuevos_frags:
            log("Muestra del texto OCR del primer doc:")
            log("   " + nuevos_frags[0]["texto"][:200].replace("\n", " "))
        log("(modo prueba: no se modifico el indice)")
        return docs_ok, len(nuevos_frags)

    if nuevos_frags:
        from sentence_transformers import SentenceTransformer
        modelo = SentenceTransformer(MODELO_EMBEDDINGS)
        log(f"  embeddings en: {modelo.device}")
        entradas = ["passage: " + f["texto"] for f in nuevos_frags]
        nv, idx_ok = encode_robusto(modelo, entradas, batch_size=32)
        if idx_ok:
            if len(idx_ok) < len(nuevos_frags):
                nuevos_frags = [nuevos_frags[i] for i in idx_ok]
            vectores = np.vstack([vectores.astype(np.float32), nv.astype(np.float32)])
            fragmentos = fragmentos + nuevos_frags
            np.save(CARPETA_INDICE / "vectores.npy", vectores)
            (CARPETA_INDICE / "fragmentos.json").write_text(
                json.dumps(fragmentos, ensure_ascii=False), encoding="utf-8")

    todos = leer_lista(PROC_PATH) | set(examinados) | {f.get("ruta") for f in fragmentos}
    PROC_PATH.write_text(json.dumps(sorted(r for r in todos if r), ensure_ascii=False),
                         encoding="utf-8")
    hechos = leer_lista(OCR_PATH) | set(examinados)
    OCR_PATH.write_text(json.dumps(sorted(hechos), ensure_ascii=False), encoding="utf-8")
    log(f"Listo: +{docs_ok} docs / +{len(nuevos_frags)} fragmentos (total {len(fragmentos)}).")
    return docs_ok, len(nuevos_frags)


if __name__ == "__main__":
    args = sys.argv[1:]
    test = 0
    if "--test" in args:
        i = args.index("--test")
        test = int(args[i + 1]) if i + 1 < len(args) else 2
        args = args[:i] + args[i + 2:]
    carpeta = next((a for a in args if not a.startswith("--")), None)
    indexar_ocr(carpeta, test=test)
