import fs from 'node:fs';
import path from 'node:path';
import { DatabaseSync } from 'node:sqlite';
import { DATA_DIR, UPLOADS_DIR, STORE_FILE } from '../config.js';

// Almacén en SQLite (viene incluido en Node, sin dependencias externas).
//
// Antes esto era un único archivo JSON que se leía COMPLETO en cada consulta.
// Con el archivo de un estudio real eso significaba parsear cientos de MB por
// pregunta. Ahora:
//   - los vectores se guardan en binario (4 bytes por número en vez de ~20),
//   - sólo se traen de disco los textos de los fragmentos que ganaron,
//   - los vectores se cargan una vez en memoria y se reusan entre consultas.

const DB_FILE = path.join(DATA_DIR, 'asistente.db');

let db = null;
let cacheVectores = null; // [{ fragId, docId, vec: Float32Array }]

function abrir() {
  if (db) return db;
  fs.mkdirSync(DATA_DIR, { recursive: true });
  fs.mkdirSync(UPLOADS_DIR, { recursive: true });

  db = new DatabaseSync(DB_FILE);
  db.exec('PRAGMA journal_mode = WAL');   // más seguro ante cortes de luz
  db.exec('PRAGMA foreign_keys = ON');
  db.exec(`
    CREATE TABLE IF NOT EXISTS documentos (
      id           TEXT PRIMARY KEY,
      nombre       TEXT NOT NULL,
      archivo      TEXT NOT NULL,
      agregado_en  TEXT NOT NULL
    );
    CREATE TABLE IF NOT EXISTS fragmentos (
      id      TEXT PRIMARY KEY,
      doc_id  TEXT NOT NULL REFERENCES documentos(id) ON DELETE CASCADE,
      indice  INTEGER NOT NULL,
      texto   TEXT NOT NULL,
      vector  BLOB,
      dim     INTEGER
    );
    CREATE INDEX IF NOT EXISTS idx_frag_doc ON fragmentos(doc_id);

    -- Mapeo de datos sensibles a códigos, para no mandar nombres reales a la IA.
    -- Varios valores pueden apuntar al MISMO código: "PEREZ, Juan Carlos",
    -- "Juan Carlos Pérez" y "Pérez" son la misma persona y deben reemplazarse
    -- todos por PERSONA_1, o el nombre se escapa por la variante no registrada.
    CREATE TABLE IF NOT EXISTS protegidos (
      valor      TEXT PRIMARY KEY,
      codigo     TEXT NOT NULL,
      tipo       TEXT NOT NULL,
      creado_en  TEXT NOT NULL
    );
    CREATE INDEX IF NOT EXISTS idx_prot_codigo ON protegidos(codigo);
  `);

  migrarDesdeJSON();
  return db;
}

// Si existe el viejo store.json, se pasa a la base y se deja de lado con otro
// nombre. Así nadie pierde los documentos que ya había indexado.
function migrarDesdeJSON() {
  if (!fs.existsSync(STORE_FILE)) return;
  try {
    const viejo = JSON.parse(fs.readFileSync(STORE_FILE, 'utf8'));
    const docs = viejo.documents || [];
    const chunks = viejo.chunks || [];
    if (docs.length) {
      console.log(`  Migrando ${docs.length} documento(s) del índice viejo a SQLite…`);
      const insDoc = db.prepare(
        'INSERT OR IGNORE INTO documentos (id, nombre, archivo, agregado_en) VALUES (?, ?, ?, ?)',
      );
      const insFrag = db.prepare(
        'INSERT OR IGNORE INTO fragmentos (id, doc_id, indice, texto, vector, dim) VALUES (?, ?, ?, ?, ?, ?)',
      );
      db.exec('BEGIN');
      for (const d of docs) {
        insDoc.run(d.id, d.name, d.fileName, d.addedAt || new Date().toISOString());
      }
      for (const c of chunks) {
        const blob = Array.isArray(c.embedding) ? aBlob(c.embedding) : null;
        insFrag.run(c.id, c.docId, c.chunkIndex, c.text, blob, blob ? c.embedding.length : null);
      }
      db.exec('COMMIT');
    }
    fs.renameSync(STORE_FILE, STORE_FILE + '.migrado');
    console.log('  ✓ Índice migrado. El archivo viejo quedó como store.json.migrado\n');
  } catch (err) {
    throw new Error(
      `No se pudo migrar el índice viejo (${STORE_FILE}): ${err.message}. ` +
        'Movelo a un lado para empezar de cero.',
    );
  }
}

// ---------- Conversión de vectores ----------

function aBlob(numeros) {
  return Buffer.from(new Float32Array(numeros).buffer);
}

function aVector(blob) {
  if (!blob) return null;
  const buf = Buffer.isBuffer(blob) ? blob : Buffer.from(blob);
  // Copiamos para no depender del buffer que devuelve SQLite.
  return new Float32Array(new Uint8Array(buf).buffer.slice(0), 0, buf.byteLength / 4);
}

// ---------- Documentos ----------

export function addDocument({ id, name, fileName, chunks }) {
  const d = abrir();
  const insDoc = d.prepare(
    'INSERT INTO documentos (id, nombre, archivo, agregado_en) VALUES (?, ?, ?, ?)',
  );
  const insFrag = d.prepare(
    'INSERT INTO fragmentos (id, doc_id, indice, texto, vector, dim) VALUES (?, ?, ?, ?, ?, ?)',
  );

  d.exec('BEGIN');
  try {
    insDoc.run(id, name, fileName, new Date().toISOString());
    for (const c of chunks) {
      const tieneVector = Array.isArray(c.embedding);
      insFrag.run(
        c.id,
        id,
        c.chunkIndex,
        c.text,
        tieneVector ? aBlob(c.embedding) : null,
        tieneVector ? c.embedding.length : null,
      );
    }
    d.exec('COMMIT');
  } catch (err) {
    d.exec('ROLLBACK');
    throw err;
  }
  cacheVectores = null;
}

export function listDocuments() {
  return abrir()
    .prepare(`
      SELECT d.id, d.nombre, d.archivo, d.agregado_en,
             COUNT(f.id) AS fragmentos,
             SUM(CASE WHEN f.vector IS NULL THEN 1 ELSE 0 END) AS sin_vector
      FROM documentos d
      LEFT JOIN fragmentos f ON f.doc_id = d.id
      GROUP BY d.id
      ORDER BY d.agregado_en DESC
    `)
    .all()
    .map((r) => ({
      id: r.id,
      name: r.nombre,
      fileName: r.archivo,
      addedAt: r.agregado_en,
      chunkCount: Number(r.fragmentos),
      sinIndexar: Number(r.sin_vector) > 0,
    }));
}

export function deleteDocument(docId) {
  const d = abrir();
  d.prepare('DELETE FROM fragmentos WHERE doc_id = ?').run(docId);
  d.prepare('DELETE FROM documentos WHERE id = ?').run(docId);
  cacheVectores = null;
}

export function documentoPorArchivo(archivo) {
  return abrir().prepare('SELECT id FROM documentos WHERE archivo = ?').get(archivo) || null;
}

export function nombresDeArchivo() {
  return abrir().prepare('SELECT archivo FROM documentos').all().map((r) => r.archivo);
}

// ---------- Búsqueda ----------

// Los vectores se cargan una sola vez y quedan en memoria: es lo que se recorre
// en cada consulta. Los textos NO se cargan acá (son la parte pesada).
function vectores() {
  if (cacheVectores) return cacheVectores;
  cacheVectores = abrir()
    .prepare('SELECT id, doc_id, vector FROM fragmentos WHERE vector IS NOT NULL')
    .all()
    .map((r) => ({ fragId: r.id, docId: r.doc_id, vec: aVector(r.vector) }));
  return cacheVectores;
}

export function vectoresDe(docIds) {
  const todos = vectores();
  if (!Array.isArray(docIds)) return todos;
  const set = new Set(docIds);
  return todos.filter((v) => set.has(v.docId));
}

// Trae el texto y la carátula sólo de los fragmentos que ganaron la búsqueda.
export function fragmentosPorId(ids) {
  if (!ids.length) return [];
  const marcas = ids.map(() => '?').join(',');
  const filas = abrir()
    .prepare(`
      SELECT f.id, f.doc_id, f.indice, f.texto, d.nombre
      FROM fragmentos f JOIN documentos d ON d.id = f.doc_id
      WHERE f.id IN (${marcas})
    `)
    .all(...ids);
  const porId = new Map(filas.map((r) => [r.id, r]));
  // Devolvemos en el mismo orden en que vinieron los ids (por relevancia).
  return ids
    .map((id) => porId.get(id))
    .filter(Boolean)
    .map((r) => ({
      id: r.id,
      docId: r.doc_id,
      docName: r.nombre,
      chunkIndex: r.indice,
      text: r.texto,
    }));
}

// Para la búsqueda por palabras: textos de los documentos elegidos.
export function fragmentosTexto(docIds) {
  const d = abrir();
  if (!Array.isArray(docIds)) {
    return d.prepare(`
      SELECT f.id, f.doc_id, f.indice, f.texto, d.nombre, f.vector IS NOT NULL AS con_vector
      FROM fragmentos f JOIN documentos d ON d.id = f.doc_id
    `).all().map(fila);
  }
  if (!docIds.length) return [];
  const marcas = docIds.map(() => '?').join(',');
  return d.prepare(`
    SELECT f.id, f.doc_id, f.indice, f.texto, d.nombre, f.vector IS NOT NULL AS con_vector
    FROM fragmentos f JOIN documentos d ON d.id = f.doc_id
    WHERE f.doc_id IN (${marcas})
  `).all(...docIds).map(fila);
}

function fila(r) {
  return {
    id: r.id,
    docId: r.doc_id,
    docName: r.nombre,
    chunkIndex: r.indice,
    text: r.texto,
    conVector: !!Number(r.con_vector),
  };
}

// Documentos elegidos que quedaron sin indexar para búsqueda por significado.
export function sinIndexar(docIds) {
  const d = abrir();
  const base = `
    SELECT DISTINCT d.nombre
    FROM fragmentos f JOIN documentos d ON d.id = f.doc_id
    WHERE f.vector IS NULL`;
  if (!Array.isArray(docIds)) return d.prepare(base).all().map((r) => r.nombre);
  if (!docIds.length) return [];
  const marcas = docIds.map(() => '?').join(',');
  return d.prepare(`${base} AND f.doc_id IN (${marcas})`).all(...docIds).map((r) => r.nombre);
}

// ---------- Datos protegidos (para el anonimizado) ----------

// Ordenados del valor más largo al más corto: así "Juan Carlos Pérez" se
// reemplaza antes que "Pérez" y no queda el nombre partido.
export function protegidosTodos() {
  return abrir()
    .prepare('SELECT valor, codigo, tipo FROM protegidos ORDER BY LENGTH(valor) DESC')
    .all();
}

export function protegidoPorValor(valor) {
  return abrir().prepare('SELECT codigo FROM protegidos WHERE valor = ?').get(valor) || null;
}

export function agregarProtegido({ codigo, valor, tipo }) {
  abrir()
    .prepare(
      'INSERT OR IGNORE INTO protegidos (valor, codigo, tipo, creado_en) VALUES (?, ?, ?, ?)',
    )
    .run(valor, codigo, tipo, new Date().toISOString());
}

// Borra el código y todas sus variantes.
export function quitarProtegido(codigo) {
  abrir().prepare('DELETE FROM protegidos WHERE codigo = ?').run(codigo);
}

// Cuenta CÓDIGOS distintos, no filas: varias variantes comparten código.
export function contarPorTipo(tipo) {
  const r = abrir()
    .prepare('SELECT COUNT(DISTINCT codigo) AS n FROM protegidos WHERE tipo = ?')
    .get(tipo);
  return Number(r?.n || 0);
}

// Para la interfaz: un renglón por código, con sus variantes juntas.
export function protegidosAgrupados() {
  const filas = abrir()
    .prepare('SELECT valor, codigo, tipo FROM protegidos ORDER BY codigo, LENGTH(valor) DESC')
    .all();
  const porCodigo = new Map();
  for (const f of filas) {
    if (!porCodigo.has(f.codigo)) {
      porCodigo.set(f.codigo, { codigo: f.codigo, tipo: f.tipo, valores: [] });
    }
    porCodigo.get(f.codigo).valores.push(f.valor);
  }
  return [...porCodigo.values()];
}
