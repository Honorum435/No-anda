import { allChunks } from './store.js';
import { embedQuery } from './embeddings.js';

function cosineSimilarity(a, b) {
  let dot = 0;
  let normA = 0;
  let normB = 0;
  for (let i = 0; i < a.length; i++) {
    dot += a[i] * b[i];
    normA += a[i] * a[i];
    normB += b[i] * b[i];
  }
  if (normA === 0 || normB === 0) return 0;
  return dot / (Math.sqrt(normA) * Math.sqrt(normB));
}

// Recupera los k fragmentos más relevantes para una pregunta.
// docIds (opcional): si se pasa, solo busca dentro de esos documentos.
export async function retrieve(query, k = 6, docIds = null) {
  let chunks = allChunks();
  if (docIds && docIds.length) {
    const set = new Set(docIds);
    chunks = chunks.filter((c) => set.has(c.docId));
  }
  if (chunks.length === 0) return [];

  const qVec = await embedQuery(query);

  return chunks
    .map((c) => ({
      docId: c.docId,
      docName: c.docName,
      chunkIndex: c.chunkIndex,
      text: c.text,
      score: cosineSimilarity(qVec, c.embedding),
    }))
    .sort((a, b) => b.score - a.score)
    .slice(0, k);
}
