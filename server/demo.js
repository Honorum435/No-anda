import {
  puedeRedactar,
  puedeBuscarPorSignificado,
  clavesQueFaltan,
  nombreProveedor,
} from './llm/provider.js';

// Cuando falta alguna clave la app sigue andando, pero recortada:
// - sin búsqueda por significado, busca por palabras clave;
// - sin modelo que redacte, muestra los pasajes encontrados y lo aclara.
// Cada carencia es independiente: con una sola clave de Gemini no falta ninguna.
export const SIN_EMBEDDINGS = !puedeBuscarPorSignificado;
export const SIN_CLAUDE = !puedeRedactar;
export const MODO_DEMO = SIN_EMBEDDINGS || SIN_CLAUDE;

// Descripción precisa de qué está recortado, para mostrarla en la interfaz.
export function estadoRecortado() {
  if (!MODO_DEMO) return null;
  const faltan = clavesQueFaltan();
  const partes = [];
  if (SIN_EMBEDDINGS) partes.push('la búsqueda es por palabras y no por significado');
  if (SIN_CLAUDE) partes.push(`${nombreProveedor} todavía no redacta las respuestas`);
  return {
    faltan,
    sinRedactar: SIN_CLAUDE,
    sinSignificado: SIN_EMBEDDINGS,
    texto:
      `Falta${faltan.length > 1 ? 'n' : ''} ${faltan.join(' y ')} en el archivo .env: ` +
      partes.join(', y ') + '.',
  };
}

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
// aclara con precisión qué clave falta para que la IA redacte de verdad.
export function respuestaDemo(fragmentos) {
  const falta = clavesQueFaltan().join(' y ') || 'la clave de la IA';

  if (fragmentos.length === 0) {
    return (
      'MODO DEMOSTRACIÓN\n\n' +
      'No encontré pasajes relacionados con esa consulta en las fuentes seleccionadas.\n\n' +
      `(Falta ${falta} en el archivo .env.)`
    );
  }

  const lista = fragmentos
    .map((f, i) => `• Pasaje [${i + 1}] de "${f.docName}" — tocá el número para leerlo.`)
    .join('\n');

  return (
    'MODO DEMOSTRACIÓN\n\n' +
    `Encontré ${fragmentos.length} pasaje(s) relacionados en tus documentos:\n\n${lista}\n\n` +
    'Acá es donde la IA redactaría la respuesta usando estos pasajes y citándolos ' +
    `con los numeritos [1] [2].\n\nPara activarla hace falta cargar ${falta} en el .env.`
  );
}
