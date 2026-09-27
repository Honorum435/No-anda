import { useRef, useState } from 'react';
import { ingestFiles, syncMega } from '../api/client';

export default function DocumentUpload({ onIndexed }) {
  const inputRef = useRef(null);
  const [subiendo, setSubiendo] = useState(false);
  const [mensaje, setMensaje] = useState('');
  const [megaLog, setMegaLog] = useState([]);

  async function handleFiles(fileList) {
    if (!fileList || fileList.length === 0) return;
    setSubiendo(true);
    setMensaje('Procesando e indexando…');
    try {
      const resultados = await ingestFiles(fileList);
      const ok = resultados.filter((r) => r.ok).length;
      const fallidos = resultados.filter((r) => !r.ok);
      let msg = `${ok} documento(s) indexado(s).`;
      if (fallidos.length) {
        msg += ' Errores: ' + fallidos.map((f) => `${f.name} (${f.error})`).join('; ');
      }
      setMensaje(msg);
      onIndexed?.();
    } catch (err) {
      setMensaje(`Error: ${err.message}`);
    } finally {
      setSubiendo(false);
      if (inputRef.current) inputRef.current.value = '';
    }
  }

  async function handleMega() {
    setSubiendo(true);
    setMegaLog([]);
    try {
      await syncMega((linea) => setMegaLog((l) => [...l, linea]));
      onIndexed?.();
    } catch (err) {
      setMegaLog((l) => [...l, `Error: ${err.message}`]);
    } finally {
      setSubiendo(false);
    }
  }

  return (
    <div className="space-y-2">
      <input
        ref={inputRef}
        type="file"
        multiple
        accept=".pdf,.docx,.txt,.md,.png,.jpg,.jpeg,.webp"
        className="hidden"
        onChange={(e) => handleFiles(e.target.files)}
      />
      <button
        onClick={() => inputRef.current?.click()}
        disabled={subiendo}
        className="w-full px-4 py-2 rounded-lg bg-slate-800 text-white text-sm font-medium hover:bg-slate-700 disabled:opacity-50"
      >
        {subiendo ? 'Procesando…' : '+ Subir archivos'}
      </button>
      <button
        onClick={handleMega}
        disabled={subiendo}
        title="Descarga e indexa la carpeta de Mega configurada en .env"
        className="w-full px-4 py-2 rounded-lg bg-red-600 text-white text-sm font-medium hover:bg-red-500 disabled:opacity-50"
      >
        ☁ Sincronizar con Mega
      </button>
      {mensaje && <p className="text-xs text-slate-500">{mensaje}</p>}
      {megaLog.length > 0 && (
        <pre className="max-h-40 overflow-y-auto text-[11px] leading-snug bg-slate-50 rounded p-2 text-slate-600 whitespace-pre-wrap">
          {megaLog.join('\n')}
        </pre>
      )}
    </div>
  );
}
