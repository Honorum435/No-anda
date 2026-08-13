// Cliente del frontend para hablar con el backend.
// `credentials: 'include'` hace que viaje la cookie de sesión en cada pedido.

async function pedir(url, opciones = {}) {
  const res = await fetch(url, { credentials: 'include', ...opciones });
  if (!res.ok) {
    const data = await res.json().catch(() => ({}));
    const err = new Error(data.error || `Error ${res.status}`);
    err.status = res.status;
    throw err;
  }
  return res.json();
}

// ---------- Sesión ----------

export const authEstado = () => pedir('/api/auth/estado');

export const login = (usuario, password) =>
  pedir('/api/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ usuario, password }),
  });

export const setupPrimerUsuario = (usuario, password) =>
  pedir('/api/auth/setup', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ usuario, password }),
  });

export const logout = () => pedir('/api/auth/logout', { method: 'POST' });

export const listarUsuarios = () => pedir('/api/auth/usuarios').then((d) => d.usuarios);

export const crearUsuario = (usuario, password) =>
  pedir('/api/auth/usuarios', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ usuario, password }),
  });

export const eliminarUsuario = (nombre) =>
  pedir(`/api/auth/usuarios/${encodeURIComponent(nombre)}`, { method: 'DELETE' });

// ---------- Estado de la app ----------

export const appEstado = () => pedir('/api/estado');

// ---------- Documentos ----------

export const fetchDocuments = () => pedir('/api/documents').then((d) => d.documents);

export const deleteDocument = (id) =>
  pedir(`/api/documents/${id}`, { method: 'DELETE' });

export async function ingestFiles(fileList) {
  const form = new FormData();
  for (const file of fileList) form.append('files', file);
  const data = await pedir('/api/ingest', { method: 'POST', body: form });
  return data.resultados;
}

// ---------- Mega ----------

// Sincroniza Mega y entrega los mensajes de progreso línea por línea.
export async function syncMega(onLine) {
  const res = await fetch('/api/mega/sync', { method: 'POST', credentials: 'include' });
  if (!res.ok) throw new Error('No se pudo iniciar la sincronización.');
  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buf = '';
  while (true) {
    const { value, done } = await reader.read();
    if (done) break;
    buf += decoder.decode(value, { stream: true });
    let i;
    while ((i = buf.indexOf('\n')) !== -1) {
      const linea = buf.slice(0, i);
      buf = buf.slice(i + 1);
      if (linea) onLine(linea);
    }
  }
  if (buf) onLine(buf);
}

// ---------- Chat ----------

// Protocolo: la primera línea del cuerpo es un JSON { citas }, el resto es texto.
// onToken(textoParcial) se llama por cada fragmento; devuelve { citas }.
export async function sendChat({ pregunta, modo, historial, docIds }, onToken) {
  const res = await fetch('/api/chat', {
    method: 'POST',
    credentials: 'include',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ pregunta, modo, historial, docIds }),
  });

  if (!res.ok) {
    const data = await res.json().catch(() => ({}));
    throw new Error(data.error || 'Error en la consulta.');
  }

  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let citas = [];
  let headerDone = false;
  let buffer = '';

  while (true) {
    const { value, done } = await reader.read();
    if (done) break;
    const trozo = decoder.decode(value, { stream: true });

    if (!headerDone) {
      buffer += trozo;
      const nl = buffer.indexOf('\n');
      if (nl === -1) continue;
      try {
        citas = JSON.parse(buffer.slice(0, nl)).citas || [];
      } catch {
        citas = [];
      }
      headerDone = true;
      const resto = buffer.slice(nl + 1);
      if (resto) onToken(resto);
    } else {
      onToken(trozo);
    }
  }

  return { citas };
}
