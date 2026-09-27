#!/usr/bin/env node
// Lista los modelos de Gemini que tu clave tiene habilitados.
//   npm run modelos
// Útil cuando un nombre de modelo quedó viejo y la app devuelve error 404.
import { listModels } from '../llm/gemini.js';
import { GEMINI_MODEL, GEMINI_EMBED_MODEL } from '../config.js';

try {
  const modelos = await listModels();

  const redactan = modelos.filter((m) => m.metodos.includes('generateContent'));
  const embeddings = modelos.filter((m) => m.metodos.includes('embedContent'));

  console.log('\nPara redactar respuestas y leer escaneados (GEMINI_MODEL):');
  redactan.forEach((m) => {
    console.log(`  ${m.id === GEMINI_MODEL ? '→' : ' '} ${m.id}`);
  });

  console.log('\nPara búsqueda por significado (GEMINI_EMBED_MODEL):');
  embeddings.forEach((m) => {
    console.log(`  ${m.id === GEMINI_EMBED_MODEL ? '→' : ' '} ${m.id}`);
  });

  const okChat = redactan.some((m) => m.id === GEMINI_MODEL);
  const okEmb = embeddings.some((m) => m.id === GEMINI_EMBED_MODEL);
  console.log('');
  if (okChat && okEmb) {
    console.log('✓ Los modelos configurados en tu .env están disponibles.');
  } else {
    if (!okChat) console.log(`✗ GEMINI_MODEL="${GEMINI_MODEL}" no figura en la lista.`);
    if (!okEmb) console.log(`✗ GEMINI_EMBED_MODEL="${GEMINI_EMBED_MODEL}" no figura en la lista.`);
    console.log('  Copiá uno de los de arriba al archivo .env.');
  }
  console.log('');
} catch (err) {
  console.error(`\n✗ ${err.message}\n`);
  process.exit(1);
}
