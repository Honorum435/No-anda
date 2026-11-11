"""Busca en el indice los fragmentos mas parecidos a una consulta (100% local, sin costo).

Uso:
    python src/buscar.py "nulidad de allanamiento sin orden"
"""
import json
import sys
import numpy as np

from comun import CARPETA_INDICE, MODELO_EMBEDDINGS, TOP_K

_modelo = None


def _cargar_modelo():
    global _modelo
    if _modelo is None:
        from sentence_transformers import SentenceTransformer
        _modelo = SentenceTransformer(MODELO_EMBEDDINGS)
    return _modelo


def cargar_indice():
    if not (CARPETA_INDICE / "vectores.npy").exists():
        raise SystemExit("No hay indice todavia. Corre primero: python src/indexar.py")
    vectores = np.load(CARPETA_INDICE / "vectores.npy")
    fragmentos = json.loads((CARPETA_INDICE / "fragmentos.json").read_text(encoding="utf-8"))
    return vectores, fragmentos


def buscar(consulta, k=TOP_K, rerank=False):
    vectores, fragmentos = cargar_indice()
    q = _cargar_modelo().encode(["query: " + consulta], normalize_embeddings=True)[0]
    similitudes = vectores @ q  # coseno (los vectores estan normalizados)
    n = max(k * 4, 25) if rerank else k
    mejores = np.argsort(-similitudes)[:n]
    candidatos = [{"score": float(similitudes[i]), **fragmentos[i]} for i in mejores]
    if rerank and len(candidatos) > k:
        try:
            from rerank import rerankear
            return rerankear(consulta, candidatos, k)
        except Exception:
            return candidatos[:k]
    return candidatos[:k]


if __name__ == "__main__":
    consulta = " ".join(sys.argv[1:]) or "nulidad de allanamiento sin orden judicial"
    print(f"Consulta: {consulta}\n")
    for r in buscar(consulta):
        print(f"[{r['score']:.3f}] {r['nombre']}")
        print(f"    {r['texto'][:250].strip()}...\n")
