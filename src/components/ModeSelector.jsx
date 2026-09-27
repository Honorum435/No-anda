const MODOS = [
  { id: 'preguntar', label: 'Preguntar', desc: 'Responde dudas sobre los casos' },
  { id: 'redactar', label: 'Redactar', desc: 'Genera borradores de escritos' },
  { id: 'precedentes', label: 'Precedentes', desc: 'Busca casos similares' },
  { id: 'resumir', label: 'Resumir', desc: 'Resume juicios largos' },
];

export default function ModeSelector({ modo, onChange }) {
  return (
    <div className="flex flex-wrap gap-2">
      {MODOS.map((m) => (
        <button
          key={m.id}
          onClick={() => onChange(m.id)}
          title={m.desc}
          className={`px-3 py-1.5 rounded-full text-sm font-medium transition ${
            modo === m.id
              ? 'bg-slate-800 text-white'
              : 'bg-white text-slate-600 hover:bg-slate-100'
          }`}
        >
          {m.label}
        </button>
      ))}
    </div>
  );
}
