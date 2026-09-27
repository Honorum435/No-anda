import { vectoresDe, fragmentosPorId, fragmentosTexto, sinIndexar } from './store.js';
import { embedQuery } from './embeddings.js';
import { SIN_EMBEDDINGS, buscarPorPalabras } from '../demo.js';

// Similitud coseno entre un Float32Array y otro.
function coseno(a, b) {
  const n = Math.min(a.length, b.length);
  let dot = 0, na = 0, nb = 0;
  for (let i = 0; i < n; i++) {
    dot += a[i] * b[i];
    na += a[i] * a[i];
    nb += b[i] * b[i];
  }
  if (!na || !nb) return 0;
  return dot / (Math.sqrt(na) * Math.sqrt(nb));
}

// Recupera los k fragmentos más relevantes para una pregunta.
// docIds: documentos donde buscar. `null` = en todos.
// Una lista VACÍA significa "en ninguno" y devuelve cero resultados: si no,
// destildar todas las fuentes terminaría respondiendo con expedientes que el
// usuario decidió excluir.
export async function retrieve(query, k = 6, docIds = null) {
  if (Array.isArray(docIds) && docIds.length === 0) {
    return { fragmentos: [], aviso: null };
  }

  // Sin búsqueda por significado: por palabras, sobre los textos elegidos.
  if (SIN_EMBEDDINGS) {
    const textos = fragmentosTexto(docIds);
    return { fragmentos: buscarPorPalabras(textos, query, k), aviso: null };
  }

  const candidatos = vectoresDe(docIds);

  // Documentos cargados antes de tener la clave: no tienen vector. Avisamos en
  // vez de ignorarlos en silencio.
  const pendientes = sinIndexar(docIds);
  const aviso = pendientes.length
    ? `Estos documentos se cargaron sin búsqueda por significado y no entran en ` +
      `esta respuesta: ${pendientes.join(', ')}. Volvé a subirlos para incluirlos.`
    : null;

  if (candidatos.length === 0) {
    const textos = fragmentosTexto(docIds);
    return { fragmentos: buscarPorPalabras(textos, query, k), aviso };
  }

  const q = Float32Array.from(await embedQuery(query));

  const puntuados = candidatos
    .map((c) => ({ fragId: c.fragId, score: coseno(q, c.vec) }))
    .sort((a, b) => b.score - a.score)
    .slice(0, k);

  // Recién ahora traemos los textos: sólo los k que ganaron.
  const textos = fragmentosPorId(puntuados.map((p) => p.fragId));
  const scorePorId = new Map(puntuados.map((p) => [p.fragId, p.score]));

  const fragmentos = textos.map((t) => ({ ...t, score: scorePorId.get(t.id) ?? 0 }));
  return { fragmentos, aviso };
}
