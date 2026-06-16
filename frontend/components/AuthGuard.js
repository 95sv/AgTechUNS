'use client';
import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { getUsuario } from '@/lib/auth';

/**
 * Guardia de UX: si no hay sesión válida en localStorage, redirige a /login.
 * No es un control de seguridad (ver nota en lib/auth.js) — el objetivo es
 * que la navegación se comporte como la de una app con login real.
 */
export default function AuthGuard({ children }) {
  const router = useRouter();
  const [usuario, setUsuario] = useState(undefined); // undefined = todavía no se chequeó

  useEffect(() => {
    const u = getUsuario();
    if (!u) {
      router.replace('/login');
    } else {
      setUsuario(u);
    }
  }, [router]);

  if (!usuario) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-stone-50">
        <p className="text-stone-400 text-sm">Verificando sesión…</p>
      </div>
    );
  }

  return children(usuario);
}
