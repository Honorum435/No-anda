import { useEffect, useRef, useState } from 'react';
import { fetchDocuments, sendChat } from './api/client';
import ModeSelector from './components/ModeSelector';
import DocumentUpload from './components/DocumentUpload';
import DocumentLibrary from './components/DocumentLibrary';

const SUGERENCIAS = [
  '¿De qué tratan estos casos?',
  'Resumí el juicio más reciente',
  'Buscá casos similares a un despido injustificado',
  '¿Qué argumentos se usaron con más éxito?',
];

// Convierte el texto de la respuesta en React, transformando [1] o [1,2] en
// chips clicables que abren el pasaje citado.
function renderConCitas(texto, citas, onAbrir) {
  const partes = texto.split(/(\[[\d,\s]+\])/g);
  return partes.map((parte, i) => {
    const m = parte.match(/^\[([\d,\s]+)\]$/);
    if (!m) return <span key={i}>{parte}</span>;
    const nums = m[1].split(',').map((s) => parseInt(s.trim(), 10)).filter(Boolean);
    return nums.map((n) => {
      const cita = citas.find((c) => c.n === n);
      return (
        <button
          key={`${i}-${n}`}
          onClick={() => cita && onAbrir(cita)}
          title={cita ? cita.docName : ''}
          className="inline-flex items-center justify-center align-super text-[10px] font-semibold w-4 h-4 mx-0.5 rounded bg-blue-100 text-blue-700 hover:bg-blue-200"
        >
          {n}
        </button>
      );
    });
  });
}

export default function App() {
  const [documents, setDocuments] = useState([]);
  const [selectedIds, setSelectedIds] = useState([]);
  const [modo, setModo] = useState('preguntar');
  const [mensajes, setMensajes] = useState([]); // { role, content, citas? }
  const [texto, setTexto] = useState('');
  const [cargando, setCargando] = useState(false);
  const [citaActiva, setCitaActiva] = useState(null);
  const finRef = useRef(null);

  async function recargarDocs() {
    const docs = await fetchDocuments().catch(() => []);
    setDocuments(docs);
    setSelectedIds((prev) => {
      // Al cargar por primera vez, seleccionar todas.
      if (prev.length === 0) return docs.map((d) => d.id);
      return prev.filter((id) => docs.some((d) => d.id === id));
    });
  }
  useEffect(() => { recargarDocs(); }, []);
  useEffect(() => { finRef.current?.scrollIntoView({ behavior: 'smooth' }); }, [mensajes]);

  const toggleDoc = (id) =>
    setSelectedIds((s) => (s.includes(id) ? s.filter((x) => x !== id) : [...s, id]));
  const toggleAll = () =>
    setSelectedIds((s) => (s.length === documents.length ? [] : documents.map((d) => d.id)));

  async function enviar(preguntaTexto) {
    const pregunta = (preguntaTexto ?? texto).trim();
    if (!pregunta || cargando) return;
    setTexto('');
    setCargando(true);

    const historial = mensajes.map((m) => ({ role: m.role, content: m.content }));
    setMensajes((m) => [...m, { role: 'user', content: pregunta }, { role: 'assistant', content: '', citas: [] }]);

    try {
      const { citas } = await sendChat(
        { pregunta, modo, historial, docIds: selectedIds },
        (delta) => {
          setMensajes((m) => {
            const c = [...m];
            c[c.length - 1] = { ...c[c.length - 1], content: c[c.length - 1].content + delta };
            return c;
          });
        },
      );
      setMensajes((m) => {
        const c = [...m];
        c[c.length - 1] = { ...c[c.length - 1], citas };
        return c;
      });
    } catch (err) {
      setMensajes((m) => {
        const c = [...m];
        c[c.length - 1] = { role: 'assistant', content: `Error: ${err.message}`, citas: [] };
        return c;
      });
    } finally {
      setCargando(false);
    }
  }

  return (
    <div className="flex h-screen bg-slate-100 text-slate-800 font-sans text-[15px]">
      {/* Panel de fuentes */}
      <aside className="w-72 shrink-0 bg-white m-2 rounded-xl shadow-sm p-4 overflow-y-auto flex flex-col">
        <h1 className="text-base font-bold">⚖️ Asistente Legal</h1>
        <p className="text-xs text-slate-500 mb-4">Fuentes</p>
        <DocumentUpload onIndexed={recargarDocs} />
        <DocumentLibrary
          documents={documents}
          selectedIds={selectedIds}
          onToggle={toggleDoc}
          onToggleAll={toggleAll}
          onChange={recargarDocs}
        />
      </aside>

      {/* Chat */}
      <main className="flex-1 flex flex-col bg-white m-2 rounded-xl shadow-sm overflow-hidden">
        <div className="border-b border-slate-100 px-6 py-3">
          <ModeSelector modo={modo} onChange={setModo} />
        </div>

        <div className="flex-1 overflow-y-auto px-6 py-5 space-y-5">
          {mensajes.length === 0 && (
            <div className="max-w-xl mx-auto mt-10 text-center">
              <p className="text-slate-400 text-sm mb-4">
                Preguntá sobre tus juicios. Las respuestas citan el documento exacto de origen.
              </p>
              <div className="grid grid-cols-2 gap-2">
                {SUGERENCIAS.map((s) => (
                  <button
                    key={s}
                    onClick={() => enviar(s)}
                    className="text-left text-sm px-3 py-2 rounded-lg border border-slate-200 hover:bg-slate-50 text-slate-600"
                  >
                    {s}
                  </button>
                ))}
              </div>
            </div>
          )}

          {mensajes.map((m, i) => (
            <div key={i} className={m.role === 'user' ? 'text-right' : 'text-left'}>
              <div
                className={`inline-block max-w-2xl px-4 py-2.5 rounded-2xl whitespace-pre-wrap leading-relaxed ${
                  m.role === 'user' ? 'bg-blue-600 text-white' : 'bg-slate-50 border border-slate-200'
                }`}
              >
                {m.role === 'assistant'
                  ? (m.content ? renderConCitas(m.content, m.citas || [], setCitaActiva) : (cargando ? '…' : ''))
                  : m.content}
                {m.role === 'assistant' && m.citas?.length > 0 && (
                  <div className="mt-2 pt-2 border-t border-slate-200 text-xs text-slate-500">
                    {[...new Set(m.citas.map((c) => c.docName))].map((doc) => (
                      <span key={doc} className="inline-block mr-2">📄 {doc}</span>
                    ))}
                  </div>
                )}
              </div>
            </div>
          ))}
          <div ref={finRef} />
        </div>

        <div className="border-t border-slate-100 px-6 py-3 flex gap-2">
          <textarea
            value={texto}
            onChange={(e) => setTexto(e.target.value)}
            onKeyDown={(e) => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); enviar(); } }}
            rows={1}
            placeholder={selectedIds.length ? 'Escribí tu consulta…' : 'Seleccioná al menos una fuente…'}
            className="flex-1 resize-none rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-blue-500"
          />
          <button
            onClick={() => enviar()}
            disabled={cargando}
            className="px-5 rounded-lg bg-blue-600 text-white text-sm font-medium hover:bg-blue-500 disabled:opacity-50"
          >
            {cargando ? '…' : 'Enviar'}
          </button>
        </div>
      </main>

      {/* Visor de la cita seleccionada */}
      {citaActiva && (
        <aside className="w-80 shrink-0 bg-white m-2 rounded-xl shadow-sm p-4 overflow-y-auto">
          <div className="flex items-center justify-between mb-2">
            <h2 className="text-sm font-semibold">Cita [{citaActiva.n}]</h2>
            <button onClick={() => setCitaActiva(null)} className="text-slate-400 hover:text-slate-700">✕</button>
          </div>
          <p className="text-xs text-blue-700 font-medium mb-2">📄 {citaActiva.docName}</p>
          <p className="text-sm text-slate-600 whitespace-pre-wrap leading-relaxed">{citaActiva.text}</p>
        </aside>
      )}
    </div>
  );
}
