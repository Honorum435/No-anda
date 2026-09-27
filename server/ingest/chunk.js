import { CHUNK_SIZE, CHUNK_OVERLAP } from '../config.js';

// Parte un texto largo en fragmentos con solapamiento. Intenta cortar en
// límites de párrafo/oración para no partir frases a la mitad.
export function chunkText(text, { size = CHUNK_SIZE, overlap = CHUNK_OVERLAP } = {}) {
  const limpio = text.replace(/\r\n/g, '\n').replace(/\n{3,}/g, '\n\n').trim();
  if (!limpio) return [];
  if (limpio.length <= size) return [limpio];

  const fragmentos = [];
  let inicio = 0;

  while (inicio < limpio.length) {
    let fin = Math.min(inicio + size, limpio.length);

    if (fin < limpio.length) {
      // Buscar un buen punto de corte hacia atrás (párrafo, punto o espacio).
      const ventana = limpio.slice(inicio, fin);
      const corteParrafo = ventana.lastIndexOf('\n\n');
      const cortePunto = ventana.lastIndexOf('. ');
      const corteEspacio = ventana.lastIndexOf(' ');
      const corte = corteParrafo > size * 0.5
        ? corteParrafo
        : cortePunto > size * 0.5
          ? cortePunto + 1
          : corteEspacio > size * 0.5
            ? corteEspacio
            : -1;
      if (corte !== -1) fin = inicio + corte;
    }

    const fragmento = limpio.slice(inicio, fin).trim();
    if (fragmento) fragmentos.push(fragmento);

    if (fin >= limpio.length) break;
    inicio = Math.max(fin - overlap, inicio + 1);
  }

  return fragmentos;
}
