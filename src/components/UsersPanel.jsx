import { useEffect, useState } from 'react';
import { listarUsuarios, crearUsuario, eliminarUsuario } from '../api/client';

// Alta y baja de las personas del estudio que pueden entrar a la app.
export default function UsersPanel({ usuarioActual }) {
  const [abierto, setAbierto] = useState(false);
  const [usuarios, setUsuarios] = useState([]);
  const [nuevo, setNuevo] = useState('');
  const [pass, setPass] = useState('');
  const [error, setError] = useState('');

  const recargar = () => listarUsuarios().then(setUsuarios).catch(() => {});
  useEffect(() => { if (abierto) recargar(); }, [abierto]);

  async function agregar(e) {
    e.preventDefault();
    setError('');
    try {
      await crearUsuario(nuevo, pass);
      setNuevo('');
      setPass('');
      recargar();
    } catch (err) {
      setError(err.message);
    }
  }

  async function quitar(nombre) {
    try {
      await eliminarUsuario(nombre);
      recargar();
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <div className="mt-4 border-t border-slate-100 pt-3">
      <button
        onClick={() => setAbierto((a) => !a)}
        className="w-full flex items-center justify-between text-xs font-semibold uppercase text-slate-400 hover:text-slate-600"
      >
        <span>👥 Personas del estudio</span>
        <span>{abierto ? '▾' : '▸'}</span>
      </button>

      {abierto && (
        <div className="mt-2">
          <ul className="space-y-0.5 mb-2">
            {usuarios.map((u) => (
              <li key={u} className="group flex items-center gap-2 px-2 py-1 rounded text-sm hover:bg-slate-100">
                <span className="flex-1 truncate text-slate-700">
                  {u} {u === usuarioActual && <span className="text-slate-400">(vos)</span>}
                </span>
                {u !== usuarioActual && (
                  <button
                    onClick={() => quitar(u)}
                    title="Quitar acceso"
                    className="text-slate-300 hover:text-red-500 opacity-0 group-hover:opacity-100"
                  >
                    ✕
                  </button>
                )}
              </li>
            ))}
          </ul>

          <form onSubmit={agregar} className="space-y-1.5">
            <input
              value={nuevo}
              onChange={(e) => setNuevo(e.target.value)}
              placeholder="Nuevo usuario"
              className="w-full rounded border border-slate-300 px-2 py-1 text-xs"
            />
            <input
              type="password"
              value={pass}
              onChange={(e) => setPass(e.target.value)}
              placeholder="Contraseña (mín. 8)"
              className="w-full rounded border border-slate-300 px-2 py-1 text-xs"
            />
            <button className="w-full py-1 rounded bg-slate-700 text-white text-xs hover:bg-slate-600">
              Agregar persona
            </button>
          </form>

          {error && <p className="mt-1 text-xs text-red-600">{error}</p>}
        </div>
      )}
    </div>
  );
}
