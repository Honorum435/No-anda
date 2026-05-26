import fs from 'node:fs';
import { DATA_DIR, UPLOADS_DIR, STORE_FILE } from '../config.js';

// Almacén vectorial sencillo basado en un archivo JSON. Suficiente para un
// prototipo con cientos/miles de fragmentos. Cada registro guarda el texto del
// fragmento, su embedding y los metadatos del documento de origen.
//
// Estructura en disco:
// { documents: [{ id, name, fileName, addedAt, chunkCount }],
//   chunks:    [{ id, docId, chunkIndex, text, embedding }] }

function ensureDirs() {
  fs.mkdirSync(DATA_DIR, { recursive: true });
  fs.mkdirSync(UPLOADS_DIR, { recursive: true });
}

function emptyStore() {
  return { documents: [], chunks: [] };
}

function load() {
  ensureDirs();
  if (!fs.existsSync(STORE_FILE)) return emptyStore();
  try {
    return JSON.parse(fs.readFileSync(STORE_FILE, 'utf8'));
  } catch {
    return emptyStore();
  }
}

function save(store) {
  ensureDirs();
  fs.writeFileSync(STORE_FILE, JSON.stringify(store), 'utf8');
}

export function addDocument({ id, name, fileName, chunks }) {
  const store = load();
  store.documents.push({
    id,
    name,
    fileName,
    addedAt: new Date().toISOString(),
    chunkCount: chunks.length,
  });
  for (const c of chunks) store.chunks.push({ ...c, docId: id });
  save(store);
}

export function listDocuments() {
  return load().documents;
}

export function deleteDocument(docId) {
  const store = load();
  store.documents = store.documents.filter((d) => d.id !== docId);
  store.chunks = store.chunks.filter((c) => c.docId !== docId);
  save(store);
}

export function getDocument(docId) {
  return load().documents.find((d) => d.id === docId) || null;
}

// Devuelve todos los fragmentos con su embedding y el nombre del documento.
export function allChunks() {
  const store = load();
  const nameById = new Map(store.documents.map((d) => [d.id, d.name]));
  return store.chunks.map((c) => ({ ...c, docName: nameById.get(c.docId) }));
}

export function chunksByDocument(docId) {
  return load()
    .chunks.filter((c) => c.docId === docId)
    .sort((a, b) => a.chunkIndex - b.chunkIndex);
}
