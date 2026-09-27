import 'dotenv/config';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

export const PORT = process.env.PORT || 3001;
export const ANTHROPIC_API_KEY = process.env.ANTHROPIC_API_KEY;
export const VOYAGE_API_KEY = process.env.VOYAGE_API_KEY;
export const GEMINI_API_KEY = process.env.GEMINI_API_KEY;
export const MEGA_EMAIL = process.env.MEGA_EMAIL;
export const MEGA_PASSWORD = process.env.MEGA_PASSWORD;
export const MEGA_FOLDER = process.env.MEGA_FOLDER || '';

// Proveedor de IA. Si no se declara, se elige solo según las claves que haya.
// Gemini cubre las tres necesidades con una sola clave: redactar, buscar por
// significado (embeddings) y leer PDF escaneados.
export const LLM_PROVIDER =
  process.env.LLM_PROVIDER || (GEMINI_API_KEY ? 'gemini' : 'claude');

// Carpeta donde se guardan los documentos subidos y el índice vectorial.
// Está en .gitignore: nada de esto se sube al repositorio.
export const DATA_DIR = path.join(__dirname, 'data');
export const UPLOADS_DIR = path.join(DATA_DIR, 'uploads');
export const STORE_FILE = path.join(DATA_DIR, 'store.json');

// Modelo de Claude. Opus 4.7 es el más capaz para razonamiento legal.
export const CLAUDE_MODEL = process.env.CLAUDE_MODEL || 'claude-opus-4-7';

// Modelo de embeddings de Voyage optimizado para textos legales.
export const EMBEDDING_MODEL = 'voyage-law-2';

// Gemini. Los nombres de modelo cambian seguido, así que son configurables:
// si alguno da error 404, ejecutá "npm run modelos" para ver los que tu clave
// tiene habilitados y poné el que corresponda en el .env.
export const GEMINI_MODEL = process.env.GEMINI_MODEL || 'gemini-2.5-flash';
export const GEMINI_EMBED_MODEL =
  process.env.GEMINI_EMBED_MODEL || 'gemini-embedding-001';
// Dimensión de los embeddings. Menos dimensiones = índice local más liviano.
export const GEMINI_EMBED_DIM = Number(process.env.GEMINI_EMBED_DIM || 768);
export const GEMINI_BASE =
  process.env.GEMINI_BASE || 'https://generativelanguage.googleapis.com/v1beta';

// Tamaño aproximado de cada fragmento (en caracteres) y solapamiento.
export const CHUNK_SIZE = 2400;
export const CHUNK_OVERLAP = 300;

export function assertKeys() {
  if (LLM_PROVIDER === 'gemini') {
    if (!GEMINI_API_KEY) {
      console.warn(
        '\n[Aviso] Falta GEMINI_API_KEY en el .env.\n' +
          'Sin ella la app funciona en modo demostración.\n',
      );
    }
    return;
  }
  const faltan = [];
  if (!ANTHROPIC_API_KEY) faltan.push('ANTHROPIC_API_KEY');
  if (!VOYAGE_API_KEY) faltan.push('VOYAGE_API_KEY (búsqueda por significado)');
  if (faltan.length) {
    console.warn(
      `\n[Aviso] Faltan variables de entorno: ${faltan.join(', ')}.\n` +
        'Copiá .env.example a .env y completá tus claves.\n',
    );
  }
}
