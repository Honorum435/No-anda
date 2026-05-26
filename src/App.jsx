import { useEffect, useRef, useState } from 'react';
import { fetchDocuments, sendChat } from './api/client';
import ModeSelector from './components/ModeSelector';
import DocumentUpload from './components/DocumentUpload';
import DocumentLibrary from './components/DocumentLibrary';

export default function App() {
  const [documents, setDocuments] = useState([]);
  const [modo, setModo] = useState('preguntar');
  const [mensajes, setMensajes] = useState([]); // { role, content, fuentes? }
  const [texto, setTexto] = useState('');
  const [cargando, setCargando] = useState(false);
  const finRef = useRef(null);

  const recargarDocs = () => fetchDocuments().then(setDocuments).catch(() => {});
  useEffect(() => { recargarDocs(); }, []);
  useEffect(() => { finRef.current?.scrollIntoView({ behavior: 'smooth' }); }, [mensajes]);

  async function enviar() {
    const pregunta = texto.trim();
    if (!pregunta || cargando) return;
    setTexto('');
    setCargando(true);

    const historial = mensajes.map((m) => ({ role: m.role, content: m.content }));
    setMensajes((m) => [...m, { role: 'user', content: pregunta }, { role: 'assistant', content: '' }]);

    try {
      const { fuentes } = await sendChat({ pregunta, modo, historial }, (delta) => {
        setMensajes((m) => {
          const copia = [...m];
          copia[copia.length - 1] = { ...copia[copia.length - 1], content: copia[copia.length - 1].content + delta };
          return copia;
        });
      });
      setMensajes((m) => {
        const copia = [...m];
        copia[copia.length - 1] = { ...copia[copia.length - 1], fuentes };
        return copia;
      });
    } catch (err) {
      setMensajes((m) => {
        const copia = [...m];
        copia[copia.length - 1] = { role: 'assistant', content: `Error: ${err.message}` };
        return copia;
      });
    } finally {
      setCargando(false);
    }
  }

  return (
    <div className="flex h-screen bg-slate-50 text-slate-800 font-sans">
      {/* Panel lateral: documentos */}
      <aside className="w-72 shrink-0 border-r border-slate-200 bg-white p-4 overflow-y-auto">
        <h1 className="text-lg font-bold mb-1">⚖️ Asistente Legal IA</h1>
        <p className="text-xs text-slate-500 mb-4">Aprende del archivo de juicios.</p>
        <DocumentUpload onIndexed={recargarDocs} />
        <h2 className="mt-5 text-xs font-semibold uppercase text-slate-400">Juicios indexados</h2>
        <DocumentLibrary documents={documents} onChange={recargarDocs} />
      </aside>

      {/* Zona de chat */}
      <main className="flex-1 flex flex-col">
        <div className="border-b border-slate-200 bg-white px-6 py-3">
          <ModeSelector modo={modo} onChange={setModo} />
        </div>

        <div className="flex-1 overflow-y-auto px-6 py-4 space-y-4">
          {mensajes.length === 0 && (
            <p className="text-center text-slate-400 mt-10 text-sm">
              Escribe una consulta sobre los juicios. Las respuestas citan los documentos de origen.
            </p>
          )}
          {mensajes.map((m, i) => (
            <div key={i} className={m.role === 'user' ? 'text-right' : 'text-left'}>
              <div
                className={`inline-block max-w-2xl px-4 py-2.5 rounded-2xl whitespace-pre-wrap text-sm ${
                  m.role === 'user' ? 'bg-slate-800 text-white' : 'bg-white border border-slate-200'
                }`}
              >
                {m.content || (cargando ? '…' : '')}
                {m.fuentes?.length > 0 && (
                  <div className="mt-2 pt-2 border-t border-slate-100 text-xs text-slate-500">
                    Fuentes: {[...new Set(m.fuentes.map((f) => f.docName))].join(', ')}
                  </div>
                )}
              </div>
            </div>
          ))}
          <div ref={finRef} />
        </div>

        <div className="border-t border-slate-200 bg-white px-6 py-3 flex gap-2">
          <textarea
            value={texto}
            onChange={(e) => setTexto(e.target.value)}
            onKeyDown={(e) => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); enviar(); } }}
            rows={1}
            placeholder="Escribe tu consulta…"
            className="flex-1 resize-none rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-slate-500"
          />
          <button
            onClick={enviar}
            disabled={cargando}
            className="px-5 rounded-lg bg-slate-800 text-white text-sm font-medium hover:bg-slate-700 disabled:opacity-50"
          >
            {cargando ? '…' : 'Enviar'}
          </button>
        </div>
      </main>
    </div>
  );
}
