'use client';
import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { getUsuario } from '@/lib/auth';

/** Raíz del sitio: redirige según haya o no sesión. No renderiza UI propia. */
export default function Home() {
  const router = useRouter();

  useEffect(() => {
    router.replace(getUsuario() ? '/dashboard' : '/login');
  }, [router]);

  return null;
}
