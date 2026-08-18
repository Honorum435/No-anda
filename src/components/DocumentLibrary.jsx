import { deleteDocument } from '../api/client';

export default function DocumentLibrary({ documents, selectedIds, onToggle, onToggleAll, onChange }) {
  async function handleDelete(id) {
    await deleteDocument(id);
    onChange?.();
  }

  if (documents.length === 0) {
    return (
      <p className="text-xs text-slate-400 mt-3">
        Aún no hay fuentes. Subí juicios o sincronizá con Mega para que la IA aprenda de ellos.
      </p>
    );
  }

  const todos = documents.every((d) => selectedIds.includes(d.id));

  return (
    <div className="mt-3">
      <label className="flex items-center gap-2 px-2 py-1 text-xs font-medium text-slate-500 cursor-pointer">
        <input type="checkbox" checked={todos} onChange={onToggleAll} className="accent-blue-600" />
        Seleccionar todas ({documents.length})
      </label>
      <ul className="space-y-0.5 mt-1">
        {documents.map((d) => (
          <li
            key={d.id}
            className="group flex items-center gap-2 px-2 py-1.5 rounded-md hover:bg-slate-100 text-sm"
          >
            <input
              type="checkbox"
              checked={selectedIds.includes(d.id)}
              onChange={() => onToggle(d.id)}
              className="accent-blue-600 shrink-0"
            />
            <span className="truncate text-slate-700 flex-1" title={d.fileName}>
              📄 {d.name}
            </span>
            <button
              onClick={() => handleDelete(d.id)}
              title="Eliminar fuente"
              className="text-slate-300 hover:text-red-500 shrink-0 opacity-0 group-hover:opacity-100"
            >
              ✕
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}
