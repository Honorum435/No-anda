import express from 'express';
import cors from 'cors';
import multer from 'multer';
import crypto from 'node:crypto';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

import { PORT, assertKeys } from './config.js';
import { extractText } from './ingest/extract.js';
import { chunkText } from './ingest/chunk.js';
import { embedDocuments } from './rag/embeddings.js';
import { addDocument, listDocuments, deleteDocument } from './rag/store.js';
import { retrieve } from './rag/retrieve.js';
import { systemPrompt, topKFor, buildUserMessage } from './llm/prompts.js';
import { streamChat } from './llm/claude.js';
import { syncMega } from './ingest/mega.js';
import { mountAuthRoutes, requireAuth, countUsers } from './auth.js';
import { MODO_DEMO, SIN_CLAUDE, respuestaDemo } from './demo.js';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const DIST_DIR = path.join(__dirname, '..', 'dist');

assertKeys();

const app = express();
// Detrás del túnel de Cloudflare hay un proxy: necesario para leer la IP real
// y saber si la conexión original era HTTPS.
app.set('trust proxy', 1);
app.use(cors({ origin: true, credentials: true }));
app.use(express.json({ limit: '2mb' }));

const upload = multer({
  storage: multer.memoryStorage(),
  limits: { fileSize: 25 * 1024 * 1024 }, // 25 MB por archivo
});

// Rutas de login/usuarios (públicas por necesidad, con freno anti-fuerza bruta).
mountAuthRoutes(app);

// Estado general de la app (para que el frontend sepa si está en modo demo).
app.get('/api/estado', requireAuth, (_req, res) => {
  res.json({ modoDemo: MODO_DEMO });
});

// A partir de acá, TODO exige haber iniciado sesión.
app.use('/api', requireAuth);

// Indexar uno o varios documentos.
app.post('/api/ingest', upload.array('files'), async (req, res) => {
  const archivos = req.files || [];
  if (archivos.length === 0) {
    return res.status(400).json({ error: 'No se recibieron archivos.' });
  }

  const resultados = [];
  for (const file of archivos) {
    try {
      const texto = await extractText({
        buffer: file.buffer,
        originalName: file.originalname,
      });
      const fragmentos = chunkText(texto);
      if (fragmentos.length === 0) {
        resultados.push({ name: file.originalname, ok: false, error: 'No se pudo extraer texto.' });
        continue;
      }

      const embeddings = await embedDocuments(fragmentos);
      const docId = crypto.randomUUID();
      addDocument({
        id: docId,
        name: file.originalname.replace(/\.[^.]+$/, ''),
        fileName: file.originalname,
        chunks: fragmentos.map((text, i) => ({
          id: `${docId}:${i}`,
          chunkIndex: i,
          text,
          embedding: embeddings[i],
        })),
      });
      resultados.push({ name: file.originalname, ok: true, chunks: fragmentos.length });
    } catch (err) {
      resultados.push({ name: file.originalname, ok: false, error: err.message });
    }
  }

  res.json({ resultados });
});

// Listar documentos indexados.
app.get('/api/documents', (_req, res) => {
  res.json({ documents: listDocuments() });
});

// Eliminar un documento del índice.
app.delete('/api/documents/:id', (req, res) => {
  deleteDocument(req.params.id);
  res.json({ ok: true });
});

// Sincroniza la carpeta de Mega configurada en .env (progreso en streaming).
app.post('/api/mega/sync', async (_req, res) => {
  res.setHeader('Content-Type', 'text/plain; charset=utf-8');
  const send = (msg) => res.write(msg + '\n');
  try {
    await syncMega(send);
  } catch (err) {
    send(`ERROR: ${err.message}`);
  }
  res.end();
});

// Chat con RAG (respuesta en streaming).
app.post('/api/chat', async (req, res) => {
  const { pregunta, modo = 'preguntar', historial = [], docIds = null } = req.body || {};
  if (!pregunta || !pregunta.trim()) {
    return res.status(400).json({ error: 'Falta la pregunta.' });
  }

  try {
    const fragmentos = await retrieve(pregunta, topKFor(modo), docIds);

    // Protocolo: primera línea = JSON con las citas numeradas (pasaje + doc),
    // luego un salto de línea y a continuación la respuesta en streaming.
    const citas = fragmentos.map((f, i) => ({
      n: i + 1,
      docId: f.docId,
      docName: f.docName,
      text: f.text,
      score: Number(f.score.toFixed(3)),
    }));
    res.setHeader('Content-Type', 'text/plain; charset=utf-8');
    res.write(JSON.stringify({ citas }) + '\n');

    // Sin clave de Claude: respuesta de demostración con los pasajes reales.
    if (SIN_CLAUDE) {
      res.write(respuestaDemo(fragmentos));
      return res.end();
    }

    const stream = streamChat({
      system: systemPrompt(modo),
      userMessage: buildUserMessage(pregunta, fragmentos),
      history: historial,
    });

    stream.on('text', (delta) => res.write(delta));
    await stream.finalMessage();
    res.end();
  } catch (err) {
    if (!res.headersSent) {
      res.status(500).json({ error: err.message });
    } else {
      res.write(`\n\n[Error: ${err.message}]`);
      res.end();
    }
  }
});

// Cualquier ruta /api que no exista responde 404 (y no la página web).
app.use('/api', (_req, res) => res.status(404).json({ error: 'Ruta no encontrada.' }));

// Sirve el frontend ya construido (npm run build), para que el túnel exponga
// una sola dirección con la app completa.
if (fs.existsSync(DIST_DIR)) {
  app.use(express.static(DIST_DIR));
  app.get('*', (_req, res) => res.sendFile(path.join(DIST_DIR, 'index.html')));
}

app.listen(PORT, () => {
  console.log(`\n  ⚖️  Asistente Legal en http://localhost:${PORT}\n`);
  if (MODO_DEMO) {
    console.log('  🔎 MODO DEMOSTRACIÓN (faltan claves de API en .env)\n');
  }
  if (countUsers() === 0) {
    console.log('  👤 Todavía no hay usuarios. Abrí la dirección de arriba EN ESTA');
    console.log('     computadora para crear el primero.\n');
  }
  if (!fs.existsSync(DIST_DIR)) {
    console.log('  ℹ️  Sin "dist": ejecutá "npm run build" para servir la app.\n');
  }
});
