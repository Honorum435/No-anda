"""Indexa documentos: corta en fragmentos, calcula embeddings localmente y guarda el indice.

Uso:
    python src/indexar.py                      # indexa datos/ejemplos
    python src/indexar.py "C:/ruta/a/estudio"  # indexa otra carpeta
"""
import json
import sys
import numpy as np

from comun import CARPETA_EJEMPLOS, CARPETA_INDICE, MODELO_EMBEDDINGS
from extraer_texto import extraer_carpeta


def limpiar_texto(t):
    """Asegura str y elimina NUL / caracteres invalidos que rompen el tokenizer."""
    if not isinstance(t, str):
        t = str(t)
    t = t.replace("\x00", " ")
    # elimina surrogates y bytes no validos en UTF-8
    return t.encode("utf-8", "ignore").decode("utf-8", "ignore")


def cortar(texto, tam=1000, solape=150):
    fragmentos, i = [], 0
    while i < len(texto):
        fragmentos.append(texto[i:i + tam])
        i += tam - solape
    return fragmentos


def encode_robusto(modelo, entradas, batch_size=32):
    """Embebe por lotes; si un lote falla, reintenta uno por uno y saltea los problematicos.
    Devuelve (vectores, indices_ok) para mantener el alineamiento con los fragmentos."""
    vecs, idx_ok = [], []
    total = len(entradas)
    for i in range(0, total, batch_size):
        lote = entradas[i:i + batch_size]
        try:
            v = modelo.encode(lote, batch_size=batch_size,
                              normalize_embeddings=True, show_progress_bar=False)
            vecs.append(np.asarray(v, dtype=np.float32))
            idx_ok.extend(range(i, i + len(lote)))
        except Exception:
            for j, item in enumerate(lote):
                try:
                    v = modelo.encode([item], normalize_embeddings=True, show_progress_bar=False)
                    vecs.append(np.asarray(v, dtype=np.float32))
                    idx_ok.append(i + j)
                except Exception:
                    pass  # fragmento problematico -> se saltea
        if (i // batch_size) % 50 == 0:
            print(f"      embeddings: {min(i + batch_size, total)}/{total}", flush=True)
    if not vecs:
        return np.zeros((0, 0), dtype=np.float32), []
    return np.vstack(vecs), idx_ok


def indexar(carpeta_docs):
    print(f"[1/4] Leyendo documentos de: {carpeta_docs}")
    documentos = extraer_carpeta(carpeta_docs)
    print(f"      {len(documentos)} documentos con texto.")
    if not documentos:
        print("      No hay nada para indexar.")
        return

    fragmentos = []
    for d in documentos:
        texto = limpiar_texto(d["texto"])
        for frag in cortar(texto):
            frag = frag.strip()
            if frag:
                fragmentos.append({"texto": frag, "nombre": d["nombre"], "ruta": d["ruta"]})
    print(f"[2/4] {len(fragmentos)} fragmentos generados.")

    print(f"[3/4] Cargando modelo de embeddings: {MODELO_EMBEDDINGS}")
    from sentence_transformers import SentenceTransformer
    modelo = SentenceTransformer(MODELO_EMBEDDINGS)
    print(f"      Dispositivo en uso: {modelo.device}")
    entradas = ["passage: " + f["texto"] for f in fragmentos]
    vectores, idx_ok = encode_robusto(modelo, entradas, batch_size=32)
    if not idx_ok:
        print("      No se pudo embeber ningun fragmento.")
        return
    if len(idx_ok) < len(fragmentos):
        print(f"      (se saltearon {len(fragmentos) - len(idx_ok)} fragmentos problematicos)")
        fragmentos = [fragmentos[i] for i in idx_ok]

    CARPETA_INDICE.mkdir(parents=True, exist_ok=True)
    np.save(CARPETA_INDICE / "vectores.npy", np.asarray(vectores, dtype=np.float32))
    (CARPETA_INDICE / "fragmentos.json").write_text(
        json.dumps(fragmentos, ensure_ascii=False), encoding="utf-8")
    print(f"[4/4] Indice guardado en: {CARPETA_INDICE}  ({len(fragmentos)} fragmentos)")


if __name__ == "__main__":
    carpeta = sys.argv[1] if len(sys.argv) > 1 else str(CARPETA_EJEMPLOS)
    indexar(carpeta)
