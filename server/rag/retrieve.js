import { allChunks } from './store.js';
import { embedQuery } from './embeddings.js';
import { SIN_EMBEDDINGS, buscarPorPalabras } from '../demo.js';

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
// docIds: lista de documentos donde buscar. `null` significa "en todos".
// Una lista VACÍA significa "en ninguno" y devuelve cero resultados: si no,
// destildar todas las fuentes terminaría respondiendo con expedientes que el
// usuario decidió excluir.
export async function retrieve(query, k = 6, docIds = null) {
  let chunks = allChunks();

  if (Array.isArray(docIds)) {
    const set = new Set(docIds);
    chunks = chunks.filter((c) => set.has(c.docId));
  }
  if (chunks.length === 0) return { fragmentos: [], aviso: null };

  // Modo demo: sin clave de embeddings, buscamos por palabras clave.
  if (SIN_EMBEDDINGS) {
    return { fragmentos: buscarPorPalabras(chunks, query, k), aviso: null };
  }

  // Los fragmentos indexados en modo demo no tienen embedding. No podemos
  // buscarlos por significado, así que avisamos en vez de ignorarlos callados.
  const conVector = chunks.filter((c) => Array.isArray(c.embedding));
  const sinVector = chunks.filter((c) => !Array.isArray(c.embedding));

  const nombresSinIndexar = [...new Set(sinVector.map((c) => c.docName))];
  const aviso = nombresSinIndexar.length
    ? `Estos documentos se cargaron en modo demostración y todavía no están ` +
      `indexados para búsqueda por significado: ${nombresSinIndexar.join(', ')}. ` +
      `Volvé a subirlos para incluirlos.`
    : null;

  if (conVector.length === 0) {
    return { fragmentos: buscarPorPalabras(chunks, query, k), aviso };
  }

  const qVec = await embedQuery(query);

  const fragmentos = conVector
    .map((c) => ({
      docId: c.docId,
      docName: c.docName,
      chunkIndex: c.chunkIndex,
      text: c.text,
      score: cosineSimilarity(qVec, c.embedding),
    }))
    .sort((a, b) => b.score - a.score)
    .slice(0, k);

  return { fragmentos, aviso };
}
