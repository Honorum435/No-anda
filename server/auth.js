import crypto from 'node:crypto';
import fs from 'node:fs';
import path from 'node:path';
import { DATA_DIR } from './config.js';

const USERS_FILE = path.join(DATA_DIR, 'users.json');
const COOKIE = 'sesion';
const SESSION_TTL_MS = 1000 * 60 * 60 * 24 * 7; // 7 días

// ---------- Contraseñas (scrypt, del módulo crypto de Node) ----------

export function hashPassword(password) {
  const salt = crypto.randomBytes(16).toString('hex');
  const hash = crypto.scryptSync(password, salt, 64).toString('hex');
  return `${salt}:${hash}`;
}

function verifyPassword(password, stored) {
  const [salt, hash] = String(stored).split(':');
  if (!salt || !hash) return false;
  const test = crypto.scryptSync(password, salt, 64);
  const known = Buffer.from(hash, 'hex');
  if (test.length !== known.length) return false;
  return crypto.timingSafeEqual(test, known);
}

// ---------- Usuarios (archivo local, nunca se sube a git) ----------

function loadUsers() {
  try {
    return JSON.parse(fs.readFileSync(USERS_FILE, 'utf8'));
  } catch {
    return [];
  }
}

function saveUsers(users) {
  fs.mkdirSync(DATA_DIR, { recursive: true });
  fs.writeFileSync(USERS_FILE, JSON.stringify(users, null, 2), 'utf8');
}

export function countUsers() {
  return loadUsers().length;
}

export function listUsers() {
  return loadUsers().map((u) => u.username);
}

export function addUser(username, password) {
  const nombre = String(username || '').trim().toLowerCase();
  if (!nombre) throw new Error('El usuario no puede estar vacío.');
  if (!password || password.length < 8) {
    throw new Error('La contraseña debe tener al menos 8 caracteres.');
  }
  const users = loadUsers();
  if (users.some((u) => u.username === nombre)) {
    throw new Error(`El usuario "${nombre}" ya existe.`);
  }
  users.push({ username: nombre, password: hashPassword(password) });
  saveUsers(users);
  return nombre;
}

export function removeUser(username) {
  const nombre = String(username || '').trim().toLowerCase();
  const users = loadUsers();
  const quedan = users.filter((u) => u.username !== nombre);
  if (quedan.length === users.length) throw new Error(`No existe el usuario "${nombre}".`);
  saveUsers(quedan);
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
    out[parte.slice(0, i).trim()] = decodeURIComponent(parte.slice(i + 1).trim());
  }
  return out;
}

// ---------- Freno a los intentos de adivinar la contraseña ----------

const intentos = new Map(); // ip -> { count, bloqueadoHasta }
const MAX_INTENTOS = 8;
const BLOQUEO_MS = 1000 * 60 * 15; // 15 minutos

function registrarFallo(ip) {
  const e = intentos.get(ip) || { count: 0, bloqueadoHasta: 0 };
  e.count += 1;
  if (e.count >= MAX_INTENTOS) {
    e.bloqueadoHasta = Date.now() + BLOQUEO_MS;
    e.count = 0;
  }
  intentos.set(ip, e);
}

function estaBloqueado(ip) {
  const e = intentos.get(ip);
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
function esLocal(req) {
  const ip = req.socket?.remoteAddress || '';
  if (req.headers['x-forwarded-for']) return false; // llegó por el túnel
  return ip === '127.0.0.1' || ip === '::1' || ip === '::ffff:127.0.0.1';
}

export function mountAuthRoutes(app) {
  // Estado: ¿hay sesión abierta? ¿hace falta crear el primer usuario?
  app.get('/api/auth/estado', (req, res) => {
    const s = getSession(parseCookies(req)[COOKIE]);
    res.json({
      autenticado: !!s,
      usuario: s?.username || null,
      requiereSetup: countUsers() === 0,
      puedeSetup: esLocal(req),
    });
  });

  // Crear el primer usuario (solo desde esta computadora y solo si no hay ninguno).
  app.post('/api/auth/setup', (req, res) => {
    if (countUsers() > 0) {
      return res.status(400).json({ error: 'Ya existen usuarios.' });
    }
    if (!esLocal(req)) {
      return res.status(403).json({
        error: 'El primer usuario solo puede crearse desde la computadora del servidor.',
      });
    }
    try {
      const nombre = addUser(req.body?.usuario, req.body?.password);
      const token = createSession(nombre);
      setCookie(req, res, token);
      res.json({ ok: true, usuario: nombre });
    } catch (err) {
      res.status(400).json({ error: err.message });
    }
  });

  app.post('/api/auth/login', (req, res) => {
    const ip = req.headers['x-forwarded-for']?.split(',')[0].trim() || req.socket.remoteAddress;
    if (estaBloqueado(ip)) {
      return res.status(429).json({ error: 'Demasiados intentos. Esperá 15 minutos.' });
    }

    const nombre = String(req.body?.usuario || '').trim().toLowerCase();
    const password = req.body?.password || '';
    const user = loadUsers().find((u) => u.username === nombre);

    if (!user || !verifyPassword(password, user.password)) {
      registrarFallo(ip);
      return res.status(401).json({ error: 'Usuario o contraseña incorrectos.' });
    }

    intentos.delete(ip);
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

  app.post('/api/auth/usuarios', requireAuth, (req, res) => {
    try {
      res.json({ ok: true, usuario: addUser(req.body?.usuario, req.body?.password) });
    } catch (err) {
      res.status(400).json({ error: err.message });
    }
  });

  app.delete('/api/auth/usuarios/:nombre', requireAuth, (req, res) => {
    if (req.params.nombre.toLowerCase() === req.usuario) {
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
  res.cookie(COOKIE, token, {
    httpOnly: true, // el JavaScript de la página no puede leerla
    sameSite: 'lax',
    secure: req.headers['x-forwarded-proto'] === 'https',
    maxAge: SESSION_TTL_MS,
  });
}
