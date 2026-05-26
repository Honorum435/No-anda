// Cliente del frontend para hablar con el backend.

export async function fetchDocuments() {
  const res = await fetch('/api/documents');
  if (!res.ok) throw new Error('No se pudieron cargar los documentos.');
  const data = await res.json();
  return data.documents;
}

export async function ingestFiles(fileList) {
  const form = new FormData();
  for (const file of fileList) form.append('files', file);
  const res = await fetch('/api/ingest', { method: 'POST', body: form });
  if (!res.ok) {
    const data = await res.json().catch(() => ({}));
    throw new Error(data.error || 'Error al indexar los archivos.');
  }
  const data = await res.json();
  return data.resultados;
}

export async function deleteDocument(id) {
  const res = await fetch(`/api/documents/${id}`, { method: 'DELETE' });
  if (!res.ok) throw new Error('No se pudo eliminar el documento.');
}

// Envía la consulta y recibe la respuesta en streaming.
// onToken(textoParcial) se llama por cada fragmento; devuelve { fuentes }.
export async function sendChat({ pregunta, modo, historial }, onToken) {
  const res = await fetch('/api/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ pregunta, modo, historial }),
  });

  if (!res.ok) {
    const data = await res.json().catch(() => ({}));
    throw new Error(data.error || 'Error en la consulta.');
  }

  let fuentes = [];
  const cabecera = res.headers.get('X-Sources');
  if (cabecera) {
    try {
      fuentes = JSON.parse(decodeURIComponent(cabecera));
    } catch {
      fuentes = [];
    }
  }

  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  while (true) {
    const { value, done } = await reader.read();
    if (done) break;
    onToken(decoder.decode(value, { stream: true }));
  }

  return { fuentes };
}
