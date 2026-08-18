import { VOYAGE_API_KEY, EMBEDDING_MODEL } from '../config.js';

const VOYAGE_URL = 'https://api.voyageai.com/v1/embeddings';

// Genera embeddings con Voyage AI. input_type distingue entre indexar
// documentos ("document") y consultar ("query"), lo que mejora la búsqueda.
async function embed(texts, inputType) {
  if (!VOYAGE_API_KEY) {
    throw new Error('Falta VOYAGE_API_KEY. Configúrala en el archivo .env.');
  }
  const res = await fetch(VOYAGE_URL, {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${VOYAGE_API_KEY}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      input: texts,
      model: EMBEDDING_MODEL,
      input_type: inputType,
    }),
  });

  if (!res.ok) {
    const detalle = await res.text().catch(() => '');
    throw new Error(`Error de Voyage (${res.status}): ${detalle}`);
  }

  const data = await res.json();
  return data.data.map((d) => d.embedding);
}

// Voyage acepta lotes; los partimos para no exceder límites de la API.
// En modo demo (sin clave) devolvemos null: los fragmentos se guardan igual y
// la búsqueda cae a palabras clave.
export async function embedDocuments(texts) {
  if (!VOYAGE_API_KEY) return texts.map(() => null);
  const LOTE = 64;
  const out = [];
  for (let i = 0; i < texts.length; i += LOTE) {
    const lote = texts.slice(i, i + LOTE);
    out.push(...(await embed(lote, 'document')));
  }
  return out;
}

export async function embedQuery(text) {
  const [v] = await embed([text], 'query');
  return v;
}
