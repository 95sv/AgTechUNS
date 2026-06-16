'use client';
import { useRef, useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useGSAP, gsap } from '@/lib/gsapSetup';
import { clearToken } from '@/lib/auth';
import ParcelaSelector from './ParcelaSelector';

export default function Header({ parcelas, seleccionadas, onChangeSeleccion, onEvaluar, evaluando, usuario }) {
  const router = useRouter();
  const headerRef = useRef(null);
  const [menuOpen, setMenuOpen] = useState(false);

  useGSAP(() => {
    gsap.from(headerRef.current, { opacity: 0, y: -16, duration: 0.5, ease: 'power2.out' });
  }, []);

  function logout() {
    clearToken();
    router.push('/login');
  }

  return (
    <header ref={headerRef} className="bg-white border-b border-stone-200">
      <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between gap-4">
        <Link href="/dashboard" className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-emerald-600 flex items-center justify-center text-white text-xl font-bold">
            🌾
          </div>
          <div>
            <h1 className="text-xl font-semibold text-stone-900">AgTechUNS</h1>
            <p className="text-xs text-stone-500">Panel de Control — Comisión 13 · UNS 2026</p>
          </div>
        </Link>

        <div className="flex items-center gap-3">
          <Link
            href="/diagnostico"
            className="hidden sm:inline text-xs text-stone-500 hover:text-emerald-700 transition px-2"
          >
            Diagnóstico
          </Link>

          <ParcelaSelector parcelas={parcelas} seleccionadas={seleccionadas} onChange={onChangeSeleccion} />

          <button
            onClick={onEvaluar}
            disabled={evaluando}
            className="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 disabled:bg-stone-300 text-white text-sm font-medium rounded-lg transition shadow-sm"
          >
            {evaluando ? 'Procesando…' : '⚡ Evaluar análisis'}
          </button>

          <div className="relative">
            <button
              onClick={() => setMenuOpen((o) => !o)}
              className="w-9 h-9 rounded-full bg-stone-100 hover:bg-stone-200 flex items-center justify-center text-sm font-semibold text-stone-700 transition"
              title={usuario?.email}
            >
              {usuario?.email?.[0]?.toUpperCase() ?? '?'}
            </button>
            {menuOpen && (
              <div className="absolute right-0 mt-2 w-56 bg-white rounded-xl border border-stone-200 shadow-lg z-20 p-3">
                <p className="text-sm font-medium text-stone-900 truncate">{usuario?.email}</p>
                <p className="text-xs text-stone-500 mb-3">{usuario?.roles?.join(', ')}</p>
                <button
                  onClick={logout}
                  className="w-full text-left text-sm text-red-600 hover:bg-red-50 rounded-lg px-2 py-1.5 transition"
                >
                  Cerrar sesión
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    </header>
  );
}
