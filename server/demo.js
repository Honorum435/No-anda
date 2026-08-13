import { ANTHROPIC_API_KEY, VOYAGE_API_KEY } from './config.js';

// El modo demo se activa solo cuando faltan las claves de API. Permite mostrar
// la app funcionando (subir juicios, buscar, ver citas) sin gastar un peso.
// La búsqueda es por palabras clave en vez de por significado, y la redacción
// de la respuesta la reemplaza un aviso claro de que es una demostración.
export const SIN_EMBEDDINGS = !VOYAGE_API_KEY;
export const SIN_CLAUDE = !ANTHROPIC_API_KEY;
export const MODO_DEMO = SIN_EMBEDDINGS || SIN_CLAUDE;

const VACIAS = new Set([
  'que', 'como', 'para', 'por', 'con', 'los', 'las', 'del', 'una', 'uno',
  'esta', 'este', 'son', 'the', 'and', 'cual', 'cuales', 'sobre', 'entre',
  'fue', 'ser', 'hay', 'mas', 'pero', 'sus', 'les', 'lo', 'la', 'el', 'de',
  'en', 'a', 'y', 'o', 'se', 'un', 'al', 'es', 'me', 'mi', 'te', 'tu',
]);

// Pasa a minúsculas y saca los acentos, para que "acción" y "accion" coincidan.
function normalizar(texto) {
  return texto.toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '');
}

function palabras(texto) {
  return normalizar(texto)
    .split(/[^a-z0-9ñ]+/)
    .filter((p) => p.length > 2 && !VACIAS.has(p));
}

// Busca los fragmentos que más palabras comparten con la pregunta.
export function buscarPorPalabras(chunks, pregunta, k) {
  const terminos = [...new Set(palabras(pregunta))];
  if (terminos.length === 0) {
    return chunks.slice(0, k).map((c) => ({ ...c, score: 0 }));
  }

  return chunks
    .map((c) => {
      const texto = normalizar(c.text);
      let aciertos = 0;
      for (const t of terminos) if (texto.includes(t)) aciertos++;
      return { ...c, score: aciertos / terminos.length };
    })
    .filter((c) => c.score > 0)
    .sort((a, b) => b.score - a.score)
    .slice(0, k);
}

// Respuesta simulada: no inventa contenido, solo muestra lo que encontró y
// aclara que falta configurar las claves para que la IA redacte de verdad.
export function respuestaDemo(fragmentos) {
  const falta = [
    SIN_CLAUDE && 'ANTHROPIC_API_KEY',
    SIN_EMBEDDINGS && 'VOYAGE_API_KEY',
  ].filter(Boolean).join(' y ');

  if (fragmentos.length === 0) {
    return (
      '🔎 MODO DEMOSTRACIÓN\n\n' +
      'No encontré pasajes relacionados con esa consulta en las fuentes seleccionadas.\n\n' +
      `(Faltan las claves ${falta} en el archivo .env. Con ellas, la IA busca por ` +
      'significado y redacta la respuesta.)'
    );
  }

  const lista = fragmentos
    .map((f, i) => `• Pasaje [${i + 1}] de "${f.docName}" — tocá el número para leerlo.`)
    .join('\n');

  return (
    '🔎 MODO DEMOSTRACIÓN\n\n' +
    `Encontré ${fragmentos.length} pasaje(s) relacionados en tus documentos:\n\n${lista}\n\n` +
    'Acá es donde la IA redactaría la respuesta usando estos pasajes y citándolos ' +
    `con los numeritos [1] [2].\n\nPara activarla hace falta cargar ${falta} en el archivo .env.`
  );
}
