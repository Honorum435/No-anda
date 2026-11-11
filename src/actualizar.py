"""Indexado INCREMENTAL: agrega al indice SOLO los documentos nuevos (no re-procesa todo).

Detecta los archivos cuya ruta aun no figura en el indice (ni en el registro de ya-vistos),
les extrae texto, calcula embeddings y los AGREGA a vectores.npy + fragmentos.json.

Limitacion: detecta NUEVOS por ruta. Un documento ya indexado que cambio de CONTENIDO no se
vuelve a procesar (para eso, reindexado completo con indexar.py).

Los PDF escaneados (sin texto) quedan registrados como examinados, pero sin fragmentos:
el paso de OCR (ocr.py) los detecta justamente por eso y los lee despues.

Uso:
    python src/actualizar.py                 # carpeta por defecto (datos/drive_casos/MochiPato)
    python src/actualizar.py --dry-run       # informa que haria, sin tocar nada
    python src/actualizar.py "C:/otra/carpeta"
"""
import json
import sys
from pathlib import Path

import numpy as np

from comun import BASE, CARPETA_INDICE, MODELO_EMBEDDINGS, clave_ruta
from extraer_texto import extraer_texto, EXTENSIONES
from indexar import limpiar_texto, cortar, encode_robusto

CARPETA_DRIVE = BASE / "datos" / "drive_casos" / "MochiPato"
PROC_PATH = CARPETA_INDICE / "procesados.json"


def _cargar_indice():
    vp = CARPETA_INDICE / "vectores.npy"
    fp = CARPETA_INDICE / "fragmentos.json"
    if not vp.exists() or not fp.exists():
        return None, None
    return np.load(vp), json.loads(fp.read_text(encoding="utf-8"))


def leer_lista(ruta):
    """Lista de rutas guardada en JSON (procesados, OCR hechos); vacia si no esta."""
    try:
        return set(json.loads(Path(ruta).read_text(encoding="utf-8")))
    except Exception:
        return set()


def _ya_vistos(fragmentos):
    """Rutas ya indexadas + las registradas como examinadas aunque no tuvieran texto,
    tal como se guardaron. Para comparar, pasarlas por clave_ruta()."""
    vistos = {f.get("ruta") for f in fragmentos if f.get("ruta")}
    return vistos | leer_lista(PROC_PATH)


def actualizar_incremental(carpeta=None, dry_run=False, log=print, parar=None):
    """Agrega al indice los documentos nuevos. Devuelve (docs_nuevos, fragmentos_nuevos).
    Con dry_run=True solo informa, sin cargar el modelo ni tocar el indice."""
    carpeta = Path(carpeta) if carpeta else CARPETA_DRIVE
    vectores, fragmentos = _cargar_indice()
    if vectores is None:
        log("No hay indice base. Corre primero el indexado completo: python src/indexar.py")
        return 0, 0

    vistos = _ya_vistos(fragmentos)
    claves = {clave_ruta(v) for v in vistos}
    archivos = [p for p in Path(carpeta).rglob("*")
                if p.is_file() and p.suffix.lower() in EXTENSIONES]
    nuevos = [p for p in archivos if clave_ruta(p) not in claves]
    log(f"[1/3] En carpeta: {len(archivos)} | ya vistos: {len(archivos) - len(nuevos)} | NUEVOS: {len(nuevos)}")
    if not nuevos:
        log("Todo al dia: no hay documentos nuevos.")
        return 0, 0

    nuevos_frags, docs_ok = [], 0
    cortado = False
    for i, p in enumerate(nuevos):
        # Punto de corte: el usuario tiene que poder frenar un indexado largo sin
        # matar el proceso. Se corta ENTRE documentos, asi lo ya procesado se guarda.
        if parar is not None and parar():
            log(f"Cancelado por el usuario: se guardan los {docs_ok} documento(s) ya procesados.")
            cortado = True
            break
        if i % 25 == 0 and i:
            log(f"   ... {i}/{len(nuevos)} documentos leidos")
        try:
            texto = limpiar_texto(extraer_texto(p))
        except Exception as e:
            log(f"   /!\\ No se pudo leer {p.suffix}: {type(e).__name__}")
            continue
        trozos = [t.strip() for t in cortar(texto) if t.strip()]
        if trozos:
            docs_ok += 1
            nuevos_frags += [{"texto": t, "nombre": p.name, "ruta": str(p)} for t in trozos]
    log(f"[2/3] {docs_ok} docs nuevos con texto -> {len(nuevos_frags)} fragmentos.")

    if dry_run:
        log("(dry-run: no se modifico el indice)")
        return docs_ok, len(nuevos_frags)

    # registrar los examinados (con o sin texto) para no re-chequearlos la proxima.
    # Si se corto, solo se marcan los que realmente se llegaron a procesar.
    procesados = {str(p) for p in nuevos[:i]} if cortado else {str(p) for p in nuevos}
    nuevos_vistos = sorted(vistos | procesados)

    if nuevos_frags:
        from sentence_transformers import SentenceTransformer
        modelo = SentenceTransformer(MODELO_EMBEDDINGS)
        log(f"      Embeddings en: {modelo.device}")
        entradas = ["passage: " + f["texto"] for f in nuevos_frags]
        nuevos_vec, idx_ok = encode_robusto(modelo, entradas, batch_size=32)
        if idx_ok:
            if len(idx_ok) < len(nuevos_frags):
                nuevos_frags = [nuevos_frags[i] for i in idx_ok]
            vectores = np.vstack([vectores.astype(np.float32), nuevos_vec.astype(np.float32)])
            fragmentos = fragmentos + nuevos_frags
            np.save(CARPETA_INDICE / "vectores.npy", vectores)
            (CARPETA_INDICE / "fragmentos.json").write_text(
                json.dumps(fragmentos, ensure_ascii=False), encoding="utf-8")

    PROC_PATH.write_text(json.dumps(nuevos_vistos, ensure_ascii=False), encoding="utf-8")
    log(f"[3/3] Listo: +{docs_ok} docs / +{len(nuevos_frags)} fragmentos (total {len(fragmentos)}).")
    return docs_ok, len(nuevos_frags)


if __name__ == "__main__":
    args = sys.argv[1:]
    dry = "--dry-run" in args
    carpeta = next((a for a in args if not a.startswith("--")), None)
    actualizar_incremental(carpeta, dry_run=dry)
