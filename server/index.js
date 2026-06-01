import express from 'express';
import cors from 'cors';
import multer from 'multer';
import crypto from 'node:crypto';

import { PORT, assertKeys } from './config.js';
import { extractText } from './ingest/extract.js';
import { chunkText } from './ingest/chunk.js';
import { embedDocuments } from './rag/embeddings.js';
import { addDocument, listDocuments, deleteDocument } from './rag/store.js';
import { retrieve } from './rag/retrieve.js';
import { systemPrompt, topKFor, buildUserMessage } from './llm/prompts.js';
import { streamChat } from './llm/claude.js';
import { syncMega } from './ingest/mega.js';

assertKeys();

const app = express();
app.use(cors());
app.use(express.json({ limit: '2mb' }));

const upload = multer({
  storage: multer.memoryStorage(),
  limits: { fileSize: 25 * 1024 * 1024 }, // 25 MB por archivo
});

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
  const { pregunta, modo = 'preguntar', historial = [] } = req.body || {};
  if (!pregunta || !pregunta.trim()) {
    return res.status(400).json({ error: 'Falta la pregunta.' });
  }

  try {
    const fragmentos = await retrieve(pregunta, topKFor(modo));

    // Las fuentes se conocen antes de generar la respuesta: las enviamos en
    // una cabecera para que el frontend las muestre junto al texto.
    const fuentes = fragmentos.map((f) => ({
      docId: f.docId,
      docName: f.docName,
      score: Number(f.score.toFixed(3)),
    }));
    res.setHeader('X-Sources', encodeURIComponent(JSON.stringify(fuentes)));
    res.setHeader('Content-Type', 'text/plain; charset=utf-8');

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

app.listen(PORT, () => {
  console.log(`\n  Servidor del asistente legal en http://localhost:${PORT}\n`);
});
