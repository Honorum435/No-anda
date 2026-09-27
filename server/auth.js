import crypto from 'node:crypto';
import fs from 'node:fs';
import path from 'node:path';
import { DATA_DIR } from './config.js';

const USERS_FILE = path.join(DATA_DIR, 'users.json');
const COOKIE = 'sesion';
const SESSION_TTL_MS = 1000 * 60 * 60 * 24 * 7; // 7 días

// ---------- Contraseñas (scrypt asíncrono) ----------
// Usamos la variante ASÍNCRONA: scryptSync tarda ~50 ms y, como Node tiene un
// solo hilo, bloquearía toda la app. Con la asíncrona el trabajo se va al
// threadpool y el servidor sigue respondiendo.

function scrypt(password, salt) {
  return new Promise((ok, ko) => {
    crypto.scrypt(password, salt, 64, (err, dk) => (err ? ko(err) : ok(dk)));
  });
}

export async function hashPassword(password) {
  const salt = crypto.randomBytes(16).toString('hex');
  const hash = (await scrypt(password, salt)).toString('hex');
  return `${salt}:${hash}`;
}

async function verifyPassword(password, stored) {
  const [salt, hash] = String(stored).split(':');
  if (!salt || !hash) return false;
  const test = await scrypt(password, salt);
  const known = Buffer.from(hash, 'hex');
  if (test.length !== known.length) return false;
  return crypto.timingSafeEqual(test, known);
}

// Hash señuelo: cuando el usuario NO existe igual gastamos el mismo tiempo,
// para que nadie pueda deducir qué usuarios existen midiendo la demora.
const HASH_SENUELO = `${'0'.repeat(32)}:${'0'.repeat(128)}`;

// ---------- Usuarios (archivo local, nunca se sube a git) ----------

let usuariosIlegibles = false;

function loadUsers() {
  if (!fs.existsSync(USERS_FILE)) {
    usuariosIlegibles = false;
    return [];
  }
  try {
    const datos = JSON.parse(fs.readFileSync(USERS_FILE, 'utf8'));
    if (!Array.isArray(datos)) throw new Error('formato inválido');
    usuariosIlegibles = false;
    return datos;
  } catch (err) {
    // El archivo existe pero no se puede leer. NO devolvemos lista vacía como
    // si no hubiera usuarios: eso reabriría la creación del administrador.
    usuariosIlegibles = true;
    console.error(`\n  ⚠️  No se pudo leer ${USERS_FILE}: ${err.message}\n`);
    return [];
  }
}

function saveUsers(users) {
  fs.mkdirSync(DATA_DIR, { recursive: true });
  // Escritura atómica: primero a un temporal y después renombramos, para que
  // un corte de luz a mitad no deje el archivo de usuarios destruido.
  const tmp = `${USERS_FILE}.tmp`;
  fs.writeFileSync(tmp, JSON.stringify(users, null, 2), 'utf8');
  fs.renameSync(tmp, USERS_FILE);
}

const normalizar = (n) => String(n || '').trim().toLowerCase();

export function countUsers() {
  return loadUsers().length;
}

export function listUsers() {
  return loadUsers().map((u) => u.username);
}

// ¿Está bloqueada la creación del primer usuario por un archivo corrupto?
export function usuariosNoLegibles() {
  loadUsers();
  return usuariosIlegibles;
}

export async function addUser(username, password) {
  const nombre = normalizar(username);
  if (!nombre) throw new Error('El usuario no puede estar vacío.');
  if (!/^[a-z0-9._-]{2,32}$/.test(nombre)) {
    throw new Error('El usuario solo puede tener letras, números, punto, guion y guion bajo.');
  }
  if (!password || password.length < 8) {
    throw new Error('La contraseña debe tener al menos 8 caracteres.');
  }
  const users = loadUsers();
  if (usuariosIlegibles) throw new Error('El archivo de usuarios está dañado.');
  if (users.some((u) => u.username === nombre)) {
    throw new Error(`El usuario "${nombre}" ya existe.`);
  }
  users.push({ username: nombre, password: await hashPassword(password) });
  saveUsers(users);
  return nombre;
}

export function removeUser(username) {
  const nombre = normalizar(username);
  const users = loadUsers();
  if (usuariosIlegibles) throw new Error('El archivo de usuarios está dañado.');
  const quedan = users.filter((u) => u.username !== nombre);
  if (quedan.length === users.length) throw new Error(`No existe el usuario "${nombre}".`);
  saveUsers(quedan);
  // Cerrar TODAS sus sesiones abiertas: si no, quien pierde el acceso podría
  // seguir entrando hasta 7 días con la cookie que ya tenía.
  for (const [token, s] of sessions) {
    if (s.username === nombre) sessions.delete(token);
  }
}

// ---------- Sesiones (en memoria: reiniciar el server cierra sesiones) ----------

const sessions = new Map(); // token -> { username, expires }

function createSession(username) {
  const token = crypto.randomBytes(32).toString('hex');
  sessions.set(token, { username, expires: Date.now() + SESSION_TTL_MS });
  return token;
}

function getSession(token) {
  if (!token) return null;
  const s = sessions.get(token);
  if (!s) return null;
  if (s.expires < Date.now()) {
    sessions.delete(token);
    return null;
  }
  return s;
}

function parseCookies(req) {
  const out = {};
  for (const parte of (req.headers.cookie || '').split(';')) {
    const i = parte.indexOf('=');
    if (i === -1) continue;
    const clave = parte.slice(0, i).trim();
    const bruto = parte.slice(i + 1).trim();
    try {
      out[clave] = decodeURIComponent(bruto);
    } catch {
      // Cookie mal formada (ej. "%zz"): la ignoramos en vez de tirar la app.
      out[clave] = bruto;
    }
  }
  return out;
}

// Limpieza periódica de sesiones vencidas y de contadores viejos.
const limpieza = setInterval(() => {
  const ahora = Date.now();
  for (const [token, s] of sessions) if (s.expires < ahora) sessions.delete(token);
  for (const [ip, e] of intentos) {
    if (e.bloqueadoHasta < ahora && e.visto < ahora - BLOQUEO_MS) intentos.delete(ip);
  }
}, 1000 * 60 * 10);
limpieza.unref?.();

// ---------- Freno a los intentos de adivinar la contraseña ----------

const intentos = new Map(); // clave -> { count, bloqueadoHasta, visto }
const MAX_INTENTOS = 8;
const BLOQUEO_MS = 1000 * 60 * 15; // 15 minutos
const MAX_CLAVES = 5000; // techo para que nadie llene la memoria

function registrarFallo(clave) {
  if (!intentos.has(clave) && intentos.size >= MAX_CLAVES) {
    // Tope alcanzado: descartamos la entrada más vieja.
    const primera = intentos.keys().next().value;
    if (primera !== undefined) intentos.delete(primera);
  }
  const e = intentos.get(clave) || { count: 0, bloqueadoHasta: 0, visto: 0 };
  e.count += 1;
  e.visto = Date.now();
  if (e.count >= MAX_INTENTOS) {
    e.bloqueadoHasta = Date.now() + BLOQUEO_MS;
    e.count = 0;
  }
  intentos.set(clave, e);
}

function estaBloqueado(clave) {
  const e = intentos.get(clave);
  return !!(e && e.bloqueadoHasta > Date.now());
}

// ---------- Middleware y rutas ----------

// Protege una ruta: si no hay sesión válida, corta con 401.
export function requireAuth(req, res, next) {
  const s = getSession(parseCookies(req)[COOKIE]);
  if (!s) return res.status(401).json({ error: 'No autorizado. Iniciá sesión.' });
  req.usuario = s.username;
  next();
}

// ¿La petición viene de la propia computadora? El primer usuario solo puede
// crearse desde acá, para que nadie pueda reclamar la app por el túnel.
// Exigimos que NO haya ninguna marca de proxy y que el socket sea local.
function esLocal(req) {
  const marcasDeProxy = [
    'x-forwarded-for',
    'x-forwarded-proto',
    'x-forwarded-host',
    'cf-connecting-ip',
    'cf-ray',
    'x-real-ip',
    'forwarded',
  ];
  if (marcasDeProxy.some((h) => req.headers[h])) return false;

  // El Host debe ser localhost: por el túnel llega el dominio público.
  const host = (req.headers.host || '').split(':')[0].toLowerCase();
  if (host !== 'localhost' && host !== '127.0.0.1' && host !== '[::1]' && host !== '::1') {
    return false;
  }

  const ip = req.socket?.remoteAddress || '';
  return ip === '127.0.0.1' || ip === '::1' || ip === '::ffff:127.0.0.1';
}

export function mountAuthRoutes(app) {
  // Estado: ¿hay sesión abierta? ¿hace falta crear el primer usuario?
  app.get('/api/auth/estado', (req, res) => {
    const s = getSession(parseCookies(req)[COOKIE]);
    res.json({
      autenticado: !!s,
      usuario: s?.username || null,
      requiereSetup: countUsers() === 0 && !usuariosIlegibles,
      puedeSetup: esLocal(req),
      archivoDanado: usuariosIlegibles,
    });
  });

  // Crear el primer usuario (solo desde esta computadora y solo si no hay ninguno).
  app.post('/api/auth/setup', async (req, res) => {
    if (!esLocal(req)) {
      return res.status(403).json({
        error: 'El primer usuario solo puede crearse desde la computadora del servidor.',
      });
    }
    if (countUsers() > 0 || usuariosIlegibles) {
      return res.status(400).json({ error: 'Ya existen usuarios.' });
    }
    try {
      const nombre = await addUser(req.body?.usuario, req.body?.password);
      setCookie(req, res, createSession(nombre));
      res.json({ ok: true, usuario: nombre });
    } catch (err) {
      res.status(400).json({ error: err.message });
    }
  });

  app.post('/api/auth/login', async (req, res) => {
    // req.ip respeta 'trust proxy' y toma la IP que puso Cloudflare, no la que
    // pudo inventar el atacante al principio de X-Forwarded-For.
    const ip = req.ip || req.socket.remoteAddress || 'desconocida';
    const nombre = normalizar(req.body?.usuario);
    const password = String(req.body?.password || '');

    // Frenamos por IP Y por usuario: así una botnet tampoco puede repartir el
    // ataque entre miles de direcciones distintas.
    if (estaBloqueado(`ip:${ip}`) || estaBloqueado(`usuario:${nombre}`)) {
      return res.status(429).json({ error: 'Demasiados intentos. Esperá 15 minutos.' });
    }

    const user = loadUsers().find((u) => u.username === nombre);
    // Si el usuario no existe verificamos igual contra un hash señuelo, para
    // que la demora sea la misma y no se pueda averiguar quién existe.
    const ok = await verifyPassword(password, user ? user.password : HASH_SENUELO);

    if (!user || !ok) {
      registrarFallo(`ip:${ip}`);
      if (nombre) registrarFallo(`usuario:${nombre}`);
      return res.status(401).json({ error: 'Usuario o contraseña incorrectos.' });
    }

    intentos.delete(`ip:${ip}`);
    intentos.delete(`usuario:${nombre}`);
    setCookie(req, res, createSession(nombre));
    res.json({ ok: true, usuario: nombre });
  });

  app.post('/api/auth/logout', (req, res) => {
    const token = parseCookies(req)[COOKIE];
    if (token) sessions.delete(token);
    res.clearCookie(COOKIE);
    res.json({ ok: true });
  });

  // Gestión de usuarios del estudio (solo para quien ya inició sesión).
  app.get('/api/auth/usuarios', requireAuth, (_req, res) => {
    res.json({ usuarios: listUsers() });
  });

  app.post('/api/auth/usuarios', requireAuth, async (req, res) => {
    try {
      res.json({ ok: true, usuario: await addUser(req.body?.usuario, req.body?.password) });
    } catch (err) {
      res.status(400).json({ error: err.message });
    }
  });

  app.delete('/api/auth/usuarios/:nombre', requireAuth, (req, res) => {
    // normalizar() también recorta espacios: sin esto, "papa%20" esquivaba
    // la comprobación de "no te elimines a vos mismo".
    if (normalizar(req.params.nombre) === req.usuario) {
      return res.status(400).json({ error: 'No podés eliminar tu propio usuario.' });
    }
    try {
      removeUser(req.params.nombre);
      res.json({ ok: true });
    } catch (err) {
      res.status(400).json({ error: err.message });
    }
  });
}

function setCookie(req, res, token) {
  // Detrás del túnel la conexión pública siempre es HTTPS; en local es HTTP.
  const esHttps =
    req.secure ||
    req.headers['x-forwarded-proto'] === 'https' ||
    !!req.headers['cf-ray'];
  res.cookie(COOKIE, token, {
    httpOnly: true, // el JavaScript de la página no puede leerla
    sameSite: 'lax', // no viaja en peticiones de otros sitios (anti-CSRF)
    secure: esHttps,
    maxAge: SESSION_TTL_MS,
  });
}
