import { useRef, useState } from 'react';
import { ingestFiles } from '../api/client';

export default function DocumentUpload({ onIndexed }) {
  const inputRef = useRef(null);
  const [subiendo, setSubiendo] = useState(false);
  const [mensaje, setMensaje] = useState('');

  async function handleFiles(fileList) {
    if (!fileList || fileList.length === 0) return;
    setSubiendo(true);
    setMensaje('Procesando e indexando… (esto puede tardar con archivos escaneados)');
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

  return (
    <div>
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
        {subiendo ? 'Indexando…' : '+ Subir juicios (PDF, Word, imagen)'}
      </button>
      {mensaje && <p className="mt-2 text-xs text-slate-500">{mensaje}</p>}
    </div>
  );
}
