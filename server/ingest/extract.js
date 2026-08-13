import mammoth from 'mammoth';
// Importamos el módulo interno para evitar el "modo debug" de pdf-parse que
// intenta leer un archivo de prueba al cargarse desde la raíz del paquete.
import pdfParse from 'pdf-parse/lib/pdf-parse.js';
import { extractTextFromDocument } from '../llm/claude.js';

// Umbral: si un PDF produce muy poco texto por página, asumimos que está
// escaneado (es una imagen) y lo pasamos al OCR con Claude.
const MIN_CHARS_POR_PAGINA = 80;

function ext(nombre) {
  const i = nombre.lastIndexOf('.');
  return i === -1 ? '' : nombre.slice(i + 1).toLowerCase();
}

async function extraerPdf(buffer) {
  let texto = '';
  let paginas = 1;
  try {
    const data = await pdfParse(buffer);
    texto = (data.text || '').trim();
    paginas = data.numpages || 1;
  } catch {
    texto = '';
  }

  // PDF escaneado (sin capa de texto): OCR con la visión de Claude.
  if (texto.length < paginas * MIN_CHARS_POR_PAGINA) {
    try {
      const ocr = await extractTextFromDocument({
        base64: buffer.toString('base64'),
        mediaType: 'application/pdf',
      });
      if (ocr && ocr.length > texto.length) return ocr;
    } catch (err) {
      // Sin clave de API (modo demo) no hay OCR. Si el PDF tenía algo de
      // texto lo aprovechamos; si no, avisamos con claridad.
      if (!texto) {
        throw new Error(
          `PDF escaneado: hace falta ANTHROPIC_API_KEY para leerlo (${err.message}).`,
        );
      }
    }
  }
  return texto;
}

const IMAGENES = {
  png: 'image/png',
  jpg: 'image/jpeg',
  jpeg: 'image/jpeg',
  webp: 'image/webp',
  gif: 'image/gif',
};

// Extrae el texto de un archivo según su tipo. Devuelve una cadena.
export async function extractText({ buffer, originalName }) {
  const e = ext(originalName);

  if (e === 'pdf') return extraerPdf(buffer);

  if (e === 'docx') {
    const { value } = await mammoth.extractRawText({ buffer });
    return (value || '').trim();
  }

  if (e === 'txt' || e === 'md') {
    return buffer.toString('utf8').trim();
  }

  if (IMAGENES[e]) {
    return extractTextFromDocument({
      base64: buffer.toString('base64'),
      mediaType: IMAGENES[e],
    });
  }

  // .doc antiguo u otros formatos no soportados directamente.
  throw new Error(
    `Formato no soportado: .${e}. Convierte el archivo a PDF, DOCX o TXT.`,
  );
}
