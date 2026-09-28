import {
  GEMINI_API_KEY,
  GEMINI_MODEL,
  GEMINI_EMBED_MODEL,
  GEMINI_EMBED_DIM,
  GEMINI_BASE,
} from '../config.js';

// Cliente de la API de Gemini por REST (sin SDK: los nombres del SDK cambian
// más seguido que los endpoints, y así no sumamos una dependencia más).

function requireKey() {
  if (!GEMINI_API_KEY) {
    throw new Error('Falta GEMINI_API_KEY. Configurala en el archivo .env.');
  }
}

async function post(path, body) {
  requireKey();
  const res = await fetch(`${GEMINI_BASE}/${path}`, {
    method: 'POST',
    headers: {
      // La clave va en la cabecera, no en la URL: así no queda escrita en logs.
      'x-goog-api-key': GEMINI_API_KEY,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(body),
  });
  if (!res.ok) throw await errorDe(res, path);
  return res;
}

async function errorDe(res, path) {
  const detalle = await res.text().catch(() => '');
  let msg;
  try {
    msg = JSON.parse(detalle)?.error?.message;
  } catch { /* texto crudo */ }
  const base = `Gemini respondió ${res.status} en ${path.split(':')[0]}`;
  if (res.status === 404) {
    return new Error(
      `${base}: el modelo no existe o tu clave no lo tiene habilitado. ` +
        'Ejecutá "npm run modelos" para ver los disponibles y ponelo en el .env.',
    );
  }
  if (res.status === 429) {
    return new Error(
      `${base}: se alcanzó el límite del plan gratuito. Esperá unos minutos.`,
    );
  }
  if (res.status === 400 && /API key/i.test(msg || detalle)) {
    return new Error(`${base}: la GEMINI_API_KEY parece inválida.`);
  }
  return new Error(`${base}${msg ? `: ${msg}` : ''}`);
}

// ---------- Listar modelos disponibles para esta clave ----------

export async function listModels() {
  requireKey();
  const res = await fetch(`${GEMINI_BASE}/models?pageSize=200`, {
    headers: { 'x-goog-api-key': GEMINI_API_KEY },
  });
  if (!res.ok) throw await errorDe(res, 'models');
  const data = await res.json();
  return (data.models || []).map((m) => ({
    id: String(m.name || '').replace(/^models\//, ''),
    metodos: m.supportedGenerationMethods || [],
  }));
}

// ---------- Redactar la respuesta (streaming) ----------

// Llama a onText(fragmento) por cada trozo y devuelve el texto completo.
export async function streamChat({ system, userMessage, history = [], onText }) {
  const contents = [
    ...history.map((m) => ({
      role: m.role === 'assistant' ? 'model' : 'user',
      parts: [{ text: m.content }],
    })),
    { role: 'user', parts: [{ text: userMessage }] },
  ];

  const res = await post(`models/${GEMINI_MODEL}:streamGenerateContent?alt=sse`, {
    systemInstruction: { parts: [{ text: system }] },
    contents,
    // temperature 0: la respuesta más probable, sin creatividad. Para citar
    // expedientes queremos exactitud y repetibilidad, no variedad.
    generationConfig: { maxOutputTokens: 4096, temperature: 0 },
  });

  let completo = '';
  for await (const trozo of leerSSE(res)) {
    const texto = (trozo.candidates?.[0]?.content?.parts || [])
      .map((p) => p.text || '')
      .join('');
    if (texto) {
      completo += texto;
      onText?.(texto);
    }
  }
  return completo;
}

// Lee un cuerpo Server-Sent Events y va entregando cada objeto JSON.
async function* leerSSE(res) {
  const decoder = new TextDecoder();
  let buffer = '';
  for await (const parte of res.body) {
    buffer += decoder.decode(parte, { stream: true });
    let corte;
    while ((corte = buffer.indexOf('\n')) !== -1) {
      const linea = buffer.slice(0, corte).trim();
      buffer = buffer.slice(corte + 1);
      if (!linea.startsWith('data:')) continue;
      const cuerpo = linea.slice(5).trim();
      if (!cuerpo || cuerpo === '[DONE]') continue;
      try {
        yield JSON.parse(cuerpo);
      } catch { /* línea parcial: la ignoramos */ }
    }
  }
}

// ---------- Leer PDF escaneados e imágenes (OCR con visión) ----------

export async function extractTextFromDocument({ base64, mediaType }) {
  const res = await post(`models/${GEMINI_MODEL}:generateContent`, {
    systemInstruction: {
      parts: [{
        text:
          'Sos un OCR experto. Extraé literalmente TODO el texto del documento, ' +
          'respetando los saltos de párrafo. No resumas, no comentes, no agregues ' +
          'nada. Devolvé solamente el texto extraído.',
      }],
    },
    contents: [{
      role: 'user',
      parts: [
        { inlineData: { mimeType: mediaType, data: base64 } },
        { text: 'Extraé todo el texto de este documento.' },
      ],
    }],
    generationConfig: { maxOutputTokens: 8192, temperature: 0 },
  });

  const data = await res.json();
  return (data.candidates?.[0]?.content?.parts || [])
    .map((p) => p.text || '')
    .join('\n')
    .trim();
}

// ---------- Embeddings (búsqueda por significado) ----------

async function embed(textos, taskType) {
  const requests = textos.map((text) => ({
    model: `models/${GEMINI_EMBED_MODEL}`,
    content: { parts: [{ text }] },
    taskType,
    outputDimensionality: GEMINI_EMBED_DIM,
  }));
  const res = await post(`models/${GEMINI_EMBED_MODEL}:batchEmbedContents`, { requests });
  const data = await res.json();
  return (data.embeddings || []).map((e) => e.values);
}

export async function embedDocuments(textos) {
  const LOTE = 32;
  const out = [];
  for (let i = 0; i < textos.length; i += LOTE) {
    out.push(...(await embed(textos.slice(i, i + LOTE), 'RETRIEVAL_DOCUMENT')));
  }
  return out;
}

export async function embedQuery(texto) {
  const [v] = await embed([texto], 'RETRIEVAL_QUERY');
  return v;
}
