"""Reordena (rerank) los candidatos con un cross-encoder multilingue LOCAL, para mas precision.

Opcional: el modelo se carga (y se descarga la primera vez) solo si se usa. Si algo falla,
el que llama deberia caer al orden por similitud vectorial.
"""
from comun import MODELO_RERANK

_modelo = None


def _cargar():
    global _modelo
    if _modelo is None:
        from sentence_transformers import CrossEncoder
        _modelo = CrossEncoder(MODELO_RERANK)
    return _modelo


def rerankear(consulta, candidatos, top_n):
    """Devuelve los top_n candidatos reordenados por el cross-encoder (mas relevante primero)."""
    if not candidatos:
        return candidatos
    pares = [(consulta, c.get("texto", "")) for c in candidatos]
    scores = _cargar().predict(pares)
    for c, s in zip(candidatos, scores):
        c["rerank_score"] = float(s)
    return sorted(candidatos, key=lambda c: c.get("rerank_score", 0.0), reverse=True)[:top_n]
