import { VOYAGE_API_KEY, EMBEDDING_MODEL } from '../config.js';
import { usaGemini, puedeBuscarPorSignificado } from '../llm/provider.js';
import * as gemini from '../llm/gemini.js';

const VOYAGE_URL = 'https://api.voyageai.com/v1/embeddings';

// Embeddings con Voyage AI. input_type distingue entre indexar documentos
// ("document") y consultar ("query"), lo que mejora la búsqueda.
async function voyage(texts, inputType) {
  const res = await fetch(VOYAGE_URL, {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${VOYAGE_API_KEY}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ input: texts, model: EMBEDDING_MODEL, input_type: inputType }),
  });

  if (!res.ok) {
    // No devolvemos el cuerpo crudo: puede traer detalles internos del servicio.
    throw new Error(
      res.status === 401
        ? 'La VOYAGE_API_KEY parece inválida.'
        : `Voyage respondió ${res.status} al generar los embeddings.`,
    );
  }

  const data = await res.json();
  return data.data.map((d) => d.embedding);
}

// Devuelve null por fragmento cuando no hay búsqueda por significado
// disponible: los fragmentos se guardan igual y la búsqueda cae a palabras.
export async function embedDocuments(texts) {
  if (!puedeBuscarPorSignificado) return texts.map(() => null);
  if (usaGemini) return gemini.embedDocuments(texts);

  const LOTE = 64;
  const out = [];
  for (let i = 0; i < texts.length; i += LOTE) {
    out.push(...(await voyage(texts.slice(i, i + LOTE), 'document')));
  }
  return out;
}

export async function embedQuery(text) {
  if (usaGemini) return gemini.embedQuery(text);
  const [v] = await voyage([text], 'query');
  return v;
}
