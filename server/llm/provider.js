import {
  LLM_PROVIDER,
  GEMINI_API_KEY,
  ANTHROPIC_API_KEY,
  VOYAGE_API_KEY,
} from '../config.js';
import * as gemini from './gemini.js';
import * as claude from './claude.js';

// Una sola puerta de entrada a la IA, para que el resto de la app no sepa ni le
// importe qué proveedor está configurado.
//
// Gemini: una clave cubre redactar, embeddings y leer escaneados.
// Claude: redacta y lee escaneados; los embeddings los da Voyage.

export const usaGemini = LLM_PROVIDER === 'gemini';

const impl = usaGemini ? gemini : claude;

// ¿Puede redactar respuestas?
export const puedeRedactar = usaGemini ? !!GEMINI_API_KEY : !!ANTHROPIC_API_KEY;

// ¿Puede leer PDF escaneados e imágenes?
export const puedeLeerEscaneados = puedeRedactar;

// ¿Puede buscar por significado (embeddings)?
export const puedeBuscarPorSignificado = usaGemini
  ? !!GEMINI_API_KEY
  : !!VOYAGE_API_KEY;

// Nombre legible del proveedor, para los mensajes de la interfaz.
export const nombreProveedor = usaGemini ? 'Gemini' : 'Claude';

// Qué claves faltan, para poder decirlo con precisión en la interfaz.
export function clavesQueFaltan() {
  if (usaGemini) return GEMINI_API_KEY ? [] : ['GEMINI_API_KEY'];
  const faltan = [];
  if (!ANTHROPIC_API_KEY) faltan.push('ANTHROPIC_API_KEY');
  if (!VOYAGE_API_KEY) faltan.push('VOYAGE_API_KEY');
  return faltan;
}

export const streamChat = (args) => impl.streamChat(args);
export const extractTextFromDocument = (args) => impl.extractTextFromDocument(args);
