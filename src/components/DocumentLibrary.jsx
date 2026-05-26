import { deleteDocument } from '../api/client';

export default function DocumentLibrary({ documents, onChange }) {
  async function handleDelete(id) {
    await deleteDocument(id);
    onChange?.();
  }

  if (documents.length === 0) {
    return (
      <p className="text-xs text-slate-400 mt-3">
        Aún no hay juicios indexados. Sube documentos para que la IA aprenda de ellos.
      </p>
    );
  }

  return (
    <ul className="mt-3 space-y-1">
      {documents.map((d) => (
        <li
          key={d.id}
          className="flex items-center justify-between gap-2 px-2 py-1.5 rounded-md hover:bg-slate-100 text-sm"
        >
          <span className="truncate text-slate-700" title={d.fileName}>
            {d.name}
            <span className="text-slate-400"> · {d.chunkCount} frag.</span>
          </span>
          <button
            onClick={() => handleDelete(d.id)}
            title="Eliminar del índice"
            className="text-slate-400 hover:text-red-500 shrink-0"
          >
            ✕
          </button>
        </li>
      ))}
    </ul>
  );
}
