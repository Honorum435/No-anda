import Anthropic from '@anthropic-ai/sdk';
import { ANTHROPIC_API_KEY, CLAUDE_MODEL } from '../config.js';

let client;
function getClient() {
  if (!ANTHROPIC_API_KEY) {
    throw new Error('Falta ANTHROPIC_API_KEY. Configúrala en el archivo .env.');
  }
  if (!client) client = new Anthropic({ apiKey: ANTHROPIC_API_KEY });
  return client;
}

// Devuelve un stream del SDK para la respuesta del chat.
// El system prompt se cachea (prompt caching) porque es estable entre peticiones.
export function streamChat({ system, userMessage, history = [] }) {
  const messages = [
    ...history.map((m) => ({ role: m.role, content: m.content })),
    { role: 'user', content: userMessage },
  ];

  return getClient().messages.stream({
    model: CLAUDE_MODEL,
    max_tokens: 8000,
    thinking: { type: 'adaptive' },
    output_config: { effort: 'high' },
    system: [{ type: 'text', text: system, cache_control: { type: 'ephemeral' } }],
    messages,
  });
}

// OCR / extracción de texto de PDFs escaneados e imágenes usando la visión de
// Claude. Evita dependencias nativas de OCR y maneja bien el español legal.
export async function extractTextFromDocument({ base64, mediaType }) {
  const source =
    mediaType === 'application/pdf'
      ? { type: 'document', source: { type: 'base64', media_type: mediaType, data: base64 } }
      : { type: 'image', source: { type: 'base64', media_type: mediaType, data: base64 } };

  const stream = getClient().messages.stream({
    model: CLAUDE_MODEL,
    max_tokens: 16000,
    system:
      'Eres un OCR experto. Extrae literalmente TODO el texto del documento, ' +
      'respetando saltos de párrafo. No resumas, no comentes, no añadas nada. ' +
      'Devuelve solo el texto extraído.',
    messages: [
      {
        role: 'user',
        content: [source, { type: 'text', text: 'Extrae todo el texto de este documento.' }],
      },
    ],
  });

  const msg = await stream.finalMessage();
  return msg.content
    .filter((b) => b.type === 'text')
    .map((b) => b.text)
    .join('\n')
    .trim();
}
