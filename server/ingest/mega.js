import crypto from 'node:crypto';
import { Storage } from 'megajs';

import { MEGA_EMAIL, MEGA_PASSWORD, MEGA_FOLDER } from '../config.js';
import { extractText } from './extract.js';
import { chunkText } from './chunk.js';
import { embedDocuments } from '../rag/embeddings.js';
import { addDocument, listDocuments } from '../rag/store.js';

const SOPORTADOS = /\.(pdf|docx|txt|md|png|jpe?g|webp|gif)$/i;

// Recorre recursivamente una carpeta de Mega y devuelve todos los archivos.
function walk(node, acc = []) {
  for (const child of node.children || []) {
    if (child.directory) walk(child, acc);
    else acc.push(child);
  }
  return acc;
}

// Sincroniza la carpeta configurada en Mega: descarga e indexa los archivos
// nuevos (los que ya están indexados se saltan por nombre).
// `onProgress(msg)` se llama con mensajes de estado para mostrar en la UI.
export async function syncMega(onProgress) {
  if (!MEGA_EMAIL || !MEGA_PASSWORD) {
    throw new Error('Faltan MEGA_EMAIL/MEGA_PASSWORD en el archivo .env.');
  }

  onProgress('Conectando a Mega…');
  const storage = await new Storage({ email: MEGA_EMAIL, password: MEGA_PASSWORD }).ready;

  let raiz = storage.root;
  if (MEGA_FOLDER) {
    const carpeta = storage.root.children?.find(
      (c) => c.directory && c.name === MEGA_FOLDER,
    );
    if (!carpeta) throw new Error(`Carpeta "${MEGA_FOLDER}" no encontrada en Mega.`);
    raiz = carpeta;
  }

  const archivos = walk(raiz).filter((f) => SOPORTADOS.test(f.name));
  const yaIndexados = new Set(listDocuments().map((d) => d.fileName));
  const nuevos = archivos.filter((f) => !yaIndexados.has(f.name));

  onProgress(`Encontrados ${archivos.length} archivos (${nuevos.length} nuevos por indexar).`);

  let okCount = 0;
  for (const archivo of nuevos) {
    try {
      onProgress(`↓ ${archivo.name}`);
      const buffer = await archivo.downloadBuffer();
      const texto = await extractText({ buffer, originalName: archivo.name });
      const fragmentos = chunkText(texto);
      if (fragmentos.length === 0) {
        onProgress(`  ✗ sin texto extraíble`);
        continue;
      }
      const embeddings = await embedDocuments(fragmentos);
      const docId = crypto.randomUUID();
      addDocument({
        id: docId,
        name: archivo.name.replace(/\.[^.]+$/, ''),
        fileName: archivo.name,
        chunks: fragmentos.map((text, i) => ({
          id: `${docId}:${i}`,
          chunkIndex: i,
          text,
          embedding: embeddings[i],
        })),
      });
      okCount++;
      onProgress(`  ✓ ${fragmentos.length} fragmentos`);
    } catch (err) {
      onProgress(`  ✗ ${err.message}`);
    }
  }

  try { await storage.close(); } catch { /* ignorar */ }
  onProgress(`FIN: ${okCount}/${nuevos.length} archivos indexados.`);
}
