import Anthropic from '@anthropic-ai/sdk';
import { ANTHROPIC_API_KEY, CLAUDE_MODEL } from '../config.js';

let client;
function getClient() {
  if (!ANTHROPIC_API_KEY) {
    throw new Error('Falta ANTHROPIC_API_KEY. Configurala en el archivo .env.');
  }
  if (!client) client = new Anthropic({ apiKey: ANTHROPIC_API_KEY });
  return client;
}

// Llama a onText(fragmento) por cada trozo y devuelve el texto completo.
// El system prompt se cachea (prompt caching) porque es estable entre pedidos.
export async function streamChat({ system, userMessage, history = [], onText }) {
  const messages = [
    ...history.map((m) => ({ role: m.role, content: m.content })),
    { role: 'user', content: userMessage },
  ];

  const stream = getClient().messages.stream({
    model: CLAUDE_MODEL,
    max_tokens: 8000,
    thinking: { type: 'adaptive' },
    output_config: { effort: 'high' },
    system: [{ type: 'text', text: system, cache_control: { type: 'ephemeral' } }],
    messages,
  });

  if (onText) stream.on('text', onText);
  const msg = await stream.finalMessage();
  return msg.content
    .filter((b) => b.type === 'text')
    .map((b) => b.text)
    .join('');
}

// OCR / extracción de texto de PDF escaneados e imágenes con la visión de Claude.
export async function extractTextFromDocument({ base64, mediaType }) {
  const source =
    mediaType === 'application/pdf'
      ? { type: 'document', source: { type: 'base64', media_type: mediaType, data: base64 } }
      : { type: 'image', source: { type: 'base64', media_type: mediaType, data: base64 } };

  const stream = getClient().messages.stream({
    model: CLAUDE_MODEL,
    max_tokens: 16000,
    system:
      'Sos un OCR experto. Extraé literalmente TODO el texto del documento, ' +
      'respetando los saltos de párrafo. No resumas, no comentes, no agregues nada. ' +
      'Devolvé solamente el texto extraído.',
    messages: [
      {
        role: 'user',
        content: [source, { type: 'text', text: 'Extraé todo el texto de este documento.' }],
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
