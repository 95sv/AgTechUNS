'use client';
import { useRef, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useGSAP, gsap } from '@/lib/gsapSetup';
import { api } from '@/lib/api';
import { saveToken } from '@/lib/auth';

const CREDENCIALES_DEMO = [
  { email: 'admin@agtech.com', password: 'admin123', rol: 'Administrador' },
  { email: 'agronomo@agtech.com', password: 'agronomo123', rol: 'Agrónomo' },
  { email: 'agricultor@agtech.com', password: 'agricultor123', rol: 'Agricultor' },
];

export default function LoginForm() {
  const router = useRouter();
  const cardRef = useRef(null);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState(null);
  const [cargando, setCargando] = useState(false);

  useGSAP(() => {
    gsap.from(cardRef.current, {
      opacity: 0,
      y: 24,
      scale: 0.97,
      duration: 0.6,
      ease: 'power3.out',
    });
  }, []);

  async function onSubmit(e) {
    e.preventDefault();
    setError(null);
    setCargando(true);
    try {
      const token = await api.login({ email, password });
      saveToken(token.access_token);
      router.push('/dashboard');
    } catch (err) {
      setError(err.message);
      gsap.fromTo(
        cardRef.current,
        { x: -8 },
        { x: 0, duration: 0.4, ease: 'elastic.out(1, 0.4)' }
      );
    } finally {
      setCargando(false);
    }
  }

  function usarDemo(cred) {
    setEmail(cred.email);
    setPassword(cred.password);
  }

  return (
    <div
      ref={cardRef}
      className="w-full max-w-md bg-white rounded-2xl border border-stone-200 shadow-lg p-8"
    >
      <div className="flex items-center gap-3 mb-6">
        <div className="w-11 h-11 rounded-xl bg-emerald-600 flex items-center justify-center text-white text-xl font-bold">
          🌾
        </div>
        <div>
          <h1 className="text-lg font-semibold text-stone-900">AgTechUNS</h1>
          <p className="text-xs text-stone-500">Iniciar sesión</p>
        </div>
      </div>

      <form onSubmit={onSubmit} className="space-y-4">
        <div>
          <label className="block text-xs font-medium text-stone-600 mb-1">Email</label>
          <input
            type="email"
            required
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="admin@agtech.com"
            className="w-full px-3 py-2 border border-stone-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500"
          />
        </div>
        <div>
          <label className="block text-xs font-medium text-stone-600 mb-1">Contraseña</label>
          <input
            type="password"
            required
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="••••••••"
            className="w-full px-3 py-2 border border-stone-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500"
          />
        </div>

        {error && (
          <p className="text-sm text-red-600 bg-red-50 border border-red-200 rounded-lg px-3 py-2">
            {error}
          </p>
        )}

        <button
          type="submit"
          disabled={cargando}
          className="w-full py-2.5 bg-emerald-600 hover:bg-emerald-700 disabled:bg-stone-300 text-white text-sm font-medium rounded-lg transition shadow-sm"
        >
          {cargando ? 'Ingresando…' : 'Ingresar'}
        </button>
      </form>

      <div className="mt-6 pt-5 border-t border-stone-100">
        <p className="text-xs text-stone-500 mb-2">Usuarios de prueba (sensores simulados):</p>
        <div className="flex flex-wrap gap-2">
          {CREDENCIALES_DEMO.map((c) => (
            <button
              key={c.email}
              type="button"
              onClick={() => usarDemo(c)}
              className="text-xs px-2.5 py-1 rounded-full bg-stone-100 hover:bg-stone-200 text-stone-700 transition"
            >
              {c.rol}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
