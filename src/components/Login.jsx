import { useState } from 'react';
import { login, setupPrimerUsuario } from '../api/client';

// Pantalla de entrada. Si todavía no hay ningún usuario creado, muestra el
// formulario de alta del primero (solo funciona desde la PC del servidor).
export default function Login({ estado, onEntrar }) {
  const setup = estado.requiereSetup;
  const [usuario, setUsuario] = useState('');
  const [password, setPassword] = useState('');
  const [password2, setPassword2] = useState('');
  const [error, setError] = useState('');
  const [enviando, setEnviando] = useState(false);

  async function enviar(e) {
    e.preventDefault();
    setError('');

    if (setup && password !== password2) {
      return setError('Las contraseñas no coinciden.');
    }

    setEnviando(true);
    try {
      if (setup) await setupPrimerUsuario(usuario, password);
      else await login(usuario, password);
      onEntrar();
    } catch (err) {
      setError(err.message);
    } finally {
      setEnviando(false);
    }
  }

  if (setup && !estado.puedeSetup) {
    return (
      <Marco>
        <p className="text-sm text-slate-600 text-center">
          Todavía no hay ningún usuario creado. Por seguridad, el primero debe crearse
          <strong> desde la computadora donde corre el servidor</strong>, no por internet.
        </p>
      </Marco>
    );
  }

  return (
    <Marco>
      <h1 className="text-xl font-bold text-center">⚖️ Asistente Legal</h1>
      <p className="text-sm text-slate-500 text-center mt-1 mb-6">
        {setup ? 'Creá el usuario administrador' : 'Ingresá para continuar'}
      </p>

      <form onSubmit={enviar} className="space-y-3">
        <input
          value={usuario}
          onChange={(e) => setUsuario(e.target.value)}
          placeholder="Usuario"
          autoComplete="username"
          className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-blue-500"
        />
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder={setup ? 'Contraseña (mínimo 8 caracteres)' : 'Contraseña'}
          autoComplete={setup ? 'new-password' : 'current-password'}
          className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-blue-500"
        />
        {setup && (
          <input
            type="password"
            value={password2}
            onChange={(e) => setPassword2(e.target.value)}
            placeholder="Repetir contraseña"
            autoComplete="new-password"
            className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-blue-500"
          />
        )}

        {error && <p className="text-sm text-red-600">{error}</p>}

        <button
          type="submit"
          disabled={enviando}
          className="w-full py-2 rounded-lg bg-blue-600 text-white text-sm font-medium hover:bg-blue-500 disabled:opacity-50"
        >
          {enviando ? 'Un momento…' : setup ? 'Crear usuario y entrar' : 'Entrar'}
        </button>
      </form>
    </Marco>
  );
}

function Marco({ children }) {
  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-100 font-sans p-4">
      <div className="w-full max-w-sm bg-white rounded-2xl shadow-sm p-8">{children}</div>
    </div>
  );
}
