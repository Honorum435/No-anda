import {
  protegidosTodos,
  protegidoPorValor,
  agregarProtegido,
  contarPorTipo,
} from './rag/store.js';

// Reemplaza datos sensibles por códigos ANTES de enviarlos a la IA, y los
// restituye en la respuesta. El proveedor de IA ve "PERSONA_1 c/ EMPRESA_2",
// nunca los nombres reales. Lo que se muestra en pantalla (los pasajes citados)
// sale de la base local y va siempre sin tocar.
//
// No es anonimato perfecto: un expediente muy particular puede ser
// identificable por su contenido. Reduce la exposición, no la elimina.

const PREFIJO = {
  persona: 'PERSONA',
  empresa: 'EMPRESA',
  dni: 'DNI',
  cuit: 'CUIT',
  email: 'EMAIL',
  telefono: 'TEL',
};

// Largo máximo de un código, para el manejo del streaming.
const MAX_CODIGO = 24;

function codigoNuevo(tipo) {
  return `${PREFIJO[tipo] || 'DATO'}_${contarPorTipo(tipo) + 1}`;
}

// Registra un valor a proteger y devuelve su código (estable entre sesiones).
// Si se pasa `codigo`, el valor se suma como variante de uno ya existente.
export function proteger(valor, tipo, codigo = null) {
  const limpio = String(valor || '').trim().replace(/\s+/g, ' ');
  if (limpio.length < 3) return null;
  const ya = protegidoPorValor(limpio);
  if (ya) return ya.codigo;
  const cod = codigo || codigoNuevo(tipo);
  agregarProtegido({ codigo: cod, valor: limpio, tipo });
  return cod;
}

// Un nombre aparece escrito de varias formas en un expediente. Si sólo
// registráramos la de la carátula, las otras viajarían sin proteger.
//   "PEREZ, Juan Carlos"  →  "Juan Carlos Perez", "Perez"
function variantesDePersona(valor) {
  const out = [];
  const m = /^([^,]+),\s*(.+)$/.exec(valor);
  if (m) {
    const apellido = m[1].trim();
    const nombres = m[2].trim();
    if (nombres && apellido) out.push(`${nombres} ${apellido}`);
    // El apellido solo, si es lo bastante distintivo para no pisar palabras
    // comunes (con menos de 4 letras el riesgo de reemplazar de más es alto).
    if (apellido.length >= 4 && !apellido.includes(' ')) out.push(apellido);
  }
  return out;
}

// Variantes de una razón social: sin el sufijo societario.
function variantesDeEmpresa(valor) {
  const sinSufijo = valor
    .replace(/[,\s]+(S\.?A\.?(\.?C\.?I\.?)?|S\.?R\.?L\.?|S\.?A\.?S\.?|S\.?H\.?)\s*$/i, '')
    .trim();
  return sinSufijo.length >= 4 && sinSufijo !== valor ? [sinSufijo] : [];
}

// Registra un nombre con todas sus variantes bajo un mismo código.
export function protegerConVariantes(valor, tipo) {
  const codigo = proteger(valor, tipo);
  if (!codigo) return null;
  const extra = tipo === 'persona' ? variantesDePersona(valor) : variantesDeEmpresa(valor);
  for (const v of extra) proteger(v, tipo, codigo);
  return codigo;
}

// ---------- Detección automática ----------

// Sólo con etiqueta explícita: un DNI suelto se confunde con un monto, y
// borrar montos por error arruinaría la utilidad de las respuestas.
const RE_DNI = /\b(?:D\.?N\.?I\.?|documento)\s*(?:n[°ºo]\s*)?:?\s*(\d{1,2}\.?\d{3}\.?\d{3})\b/gi;
const RE_CUIT = /\b(\d{2}-\d{8}-\d)\b/g;
const RE_EMAIL = /\b([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,})\b/g;
const RE_TEL = /\b(?:tel(?:éfono)?|celular|cel)\.?\s*:?\s*((?:\+?\d[\d\s().-]{6,}\d))/gi;

// Carátula al estilo argentino: "APELLIDO, Nombre c/ RAZÓN SOCIAL S.A. s/ materia"
const RE_CARATULA = /^(.{3,90}?)\s+c\/\s+(.{3,90}?)(?:\s+s\/|$)/i;

function registrarConRegex(texto, re, tipo) {
  let m;
  re.lastIndex = 0;
  while ((m = re.exec(texto)) !== null) proteger(m[1], tipo);
}

// Al indexar un documento, aprende qué hay que proteger de él.
export function registrarDesdeDocumento({ fileName, texto }) {
  const cabeza = `${fileName || ''}\n${String(texto || '').slice(0, 1500)}`;

  // Partes de la carátula, buscadas en el nombre del archivo y al comienzo.
  for (const linea of cabeza.split('\n').slice(0, 12)) {
    const m = RE_CARATULA.exec(linea.replace(/\.[a-z0-9]{2,5}$/i, '').trim());
    if (!m) continue;
    const actor = m[1].replace(/^(expediente|exp\.?)\s*[\d./-]*\s*/i, '').trim();
    const demandado = m[2].trim();
    for (const parte of [actor, demandado]) {
      if (!parte) continue;
      const esEmpresa = /\b(S\.?A\.?|S\.?R\.?L\.?|S\.?A\.?S\.?|S\.?H\.?|SACI)\.?\s*$/i.test(parte);
      protegerConVariantes(parte, esEmpresa ? 'empresa' : 'persona');
    }
  }

  // Identificadores en todo el documento.
  registrarConRegex(texto, RE_CUIT, 'cuit');
  registrarConRegex(texto, RE_DNI, 'dni');
  registrarConRegex(texto, RE_EMAIL, 'email');
  registrarConRegex(texto, RE_TEL, 'telefono');
}

// ---------- Reemplazo ----------

const ACENTOS = {
  a: '[aáàäâ]', e: '[eéèëê]', i: '[iíìïî]', o: '[oóòöô]', u: '[uúùüû]',
  n: '[nñ]', c: '[cç]',
};

// Arma una expresión que tolera acentos y mayúsculas, para que "PÉREZ",
// "Pérez" y "Perez" se reemplacen igual. Los límites evitan reemplazar dentro
// de otra palabra (que "Paz" no destroce "Lapaz" ni "capaz").
function patronFlexible(valor) {
  let out = '';
  for (const ch of valor) {
    const base = ch.toLowerCase();
    if (ACENTOS[base]) out += ACENTOS[base];
    else if (/\s/.test(ch)) out += '\\s+';
    else out += ch.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  }
  return `(?<![\\p{L}\\p{N}])${out}(?![\\p{L}\\p{N}])`;
}

// Devuelve { texto, usados } donde `usados` es el mapa código → valor real.
export function anonimizar(texto) {
  let salida = String(texto || '');
  const usados = new Map();

  // Los más largos primero: así "Juan Pérez" gana sobre "Pérez".
  for (const p of protegidosTodos()) {
    const re = new RegExp(patronFlexible(p.valor), 'giu');
    if (!re.test(salida)) continue;
    re.lastIndex = 0;
    salida = salida.replace(re, p.codigo);
    // Al restituir usamos la forma más completa que vimos de cada código:
    // si ya guardamos "PEREZ, Juan Carlos", no la pisamos con "Perez".
    const previo = usados.get(p.codigo);
    if (!previo || p.valor.length > previo.length) usados.set(p.codigo, p.valor);
  }
  return { texto: salida, usados };
}

// Restituye los valores reales en un texto ya completo.
export function restaurar(texto, usados) {
  let salida = String(texto || '');
  for (const [codigo, valor] of usados) {
    salida = salida.split(codigo).join(valor);
  }
  return salida;
}

// Restitución sobre un texto que llega de a pedazos (streaming).
// Retiene el final del buffer para no cortar un código a la mitad.
export class RestauradorStream {
  constructor(usados) {
    this.usados = usados;
    this.buf = '';
    this.enviado = 0;
  }

  // Recibe un pedazo y devuelve el texto listo para mandar al navegador.
  empujar(delta) {
    this.buf += delta;
    let corte = this.buf.length - MAX_CODIGO;
    if (corte <= this.enviado) return '';
    // Retrocede hasta un carácter que no pueda ser parte de un código, para
    // que ningún código quede partido entre dos envíos.
    while (corte > this.enviado && /[A-Z0-9_]/.test(this.buf[corte])) corte--;
    if (corte <= this.enviado) return '';
    const trozo = this.buf.slice(this.enviado, corte);
    this.enviado = corte;
    return restaurar(trozo, this.usados);
  }

  // Lo que quedó retenido al terminar.
  fin() {
    const resto = this.buf.slice(this.enviado);
    this.enviado = this.buf.length;
    return restaurar(resto, this.usados);
  }
}
