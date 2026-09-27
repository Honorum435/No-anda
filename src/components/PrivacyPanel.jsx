import { useEffect, useState } from 'react';
import { listarProtegidos, agregarProtegido, quitarProtegido } from '../api/client';

const TIPOS = [
  ['persona', 'Persona'],
  ['empresa', 'Empresa'],
  ['dni', 'DNI'],
  ['cuit', 'CUIT'],
  ['email', 'Correo'],
  ['telefono', 'Teléfono'],
];

// Muestra qué datos se reemplazan por códigos antes de enviarlos a la IA, y
// permite agregar los que la detección automática no encontró.
export default function PrivacyPanel() {
  const [abierto, setAbierto] = useState(false);
  const [datos, setDatos] = useState(null);
  const [valor, setValor] = useState('');
  const [tipo, setTipo] = useState('persona');
  const [error, setError] = useState('');

  const recargar = () => listarProtegidos().then(setDatos).catch(() => {});
  useEffect(() => { if (abierto) recargar(); }, [abierto]);

  async function agregar(e) {
    e.preventDefault();
    setError('');
    try {
      await agregarProtegido(valor, tipo);
      setValor('');
      recargar();
    } catch (err) {
      setError(err.message);
    }
  }

  async function quitar(codigo) {
    await quitarProtegido(codigo).catch(() => {});
    recargar();
  }

  return (
    <div className="mt-4 border-t border-slate-100 pt-3">
      <button
        onClick={() => setAbierto((a) => !a)}
        className="w-full flex items-center justify-between text-xs font-semibold uppercase text-slate-400 hover:text-slate-600"
      >
        <span>Datos reservados</span>
        <span>{abierto ? '▾' : '▸'}</span>
      </button>

      {abierto && (
        <div className="mt-2">
          {datos && !datos.activo && (
            <p className="text-xs text-amber-700 bg-amber-50 rounded px-2 py-1.5 mb-2">
              Desactivado: los nombres viajan tal cual. Para activarlo, quitá
              <code className="mx-1">ANONIMIZAR=no</code> del archivo .env.
            </p>
          )}

          <p className="text-[11px] text-slate-500 leading-snug mb-2">
            Esto se reemplaza por un código antes de salir de la computadora. En
            pantalla siempre ves el dato real.
          </p>

          <ul className="space-y-1 mb-2">
            {(datos?.protegidos || []).map((p) => (
              <li key={p.codigo} className="group flex items-start gap-2 text-xs">
                <code className="shrink-0 bg-slate-100 text-slate-600 rounded px-1.5 py-0.5 font-mono text-[10px]">
                  {p.codigo}
                </code>
                <span className="flex-1 min-w-0 text-slate-700 truncate" title={p.valores.join(' · ')}>
                  {p.valores[0]}
                  {p.valores.length > 1 && (
                    <span className="text-slate-400"> +{p.valores.length - 1}</span>
                  )}
                </span>
                <button
                  onClick={() => quitar(p.codigo)}
                  title="Dejar de proteger"
                  className="text-slate-300 hover:text-red-500 opacity-0 group-hover:opacity-100"
                >
                  ✕
                </button>
              </li>
            ))}
            {datos && datos.protegidos.length === 0 && (
              <li className="text-xs text-slate-400">
                Todavía nada. Se detecta solo al cargar expedientes.
              </li>
            )}
          </ul>

          <form onSubmit={agregar} className="space-y-1.5">
            <input
              value={valor}
              onChange={(e) => setValor(e.target.value)}
              placeholder="Nombre o dato a proteger"
              className="w-full rounded border border-slate-300 px-2 py-1 text-xs"
            />
            <div className="flex gap-1.5">
              <select
                value={tipo}
                onChange={(e) => setTipo(e.target.value)}
                className="rounded border border-slate-300 px-1.5 py-1 text-xs bg-white"
              >
                {TIPOS.map(([v, t]) => <option key={v} value={v}>{t}</option>)}
              </select>
              <button className="flex-1 py-1 rounded bg-slate-700 text-white text-xs hover:bg-slate-600">
                Proteger
              </button>
            </div>
          </form>

          {error && <p className="mt-1 text-xs text-red-600">{error}</p>}
        </div>
      )}
    </div>
  );
}
