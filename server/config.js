import 'dotenv/config';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

export const PORT = process.env.PORT || 3001;
export const ANTHROPIC_API_KEY = process.env.ANTHROPIC_API_KEY;
export const VOYAGE_API_KEY = process.env.VOYAGE_API_KEY;
export const MEGA_EMAIL = process.env.MEGA_EMAIL;
export const MEGA_PASSWORD = process.env.MEGA_PASSWORD;
export const MEGA_FOLDER = process.env.MEGA_FOLDER || '';

// Carpeta donde se guardan los documentos subidos y el índice vectorial.
// Está en .gitignore: nada de esto se sube al repositorio.
export const DATA_DIR = path.join(__dirname, 'data');
export const UPLOADS_DIR = path.join(DATA_DIR, 'uploads');
export const STORE_FILE = path.join(DATA_DIR, 'store.json');

// Modelo de Claude. Opus 4.7 es el más capaz para razonamiento legal.
export const CLAUDE_MODEL = 'claude-opus-4-7';

// Modelo de embeddings de Voyage optimizado para textos legales.
export const EMBEDDING_MODEL = 'voyage-law-2';

// Tamaño aproximado de cada fragmento (en caracteres) y solapamiento.
export const CHUNK_SIZE = 2400;
export const CHUNK_OVERLAP = 300;

export function assertKeys() {
  const faltan = [];
  if (!ANTHROPIC_API_KEY) faltan.push('ANTHROPIC_API_KEY');
  if (!VOYAGE_API_KEY) faltan.push('VOYAGE_API_KEY');
  if (faltan.length) {
    console.warn(
      `\n[Aviso] Faltan variables de entorno: ${faltan.join(', ')}.\n` +
        'Copia .env.example a .env y completa tus claves para usar la IA.\n',
    );
  }
}
