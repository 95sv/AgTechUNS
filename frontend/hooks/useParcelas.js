'use client';
import { useCallback, useEffect, useRef, useState } from 'react';
import { api } from '@/lib/api';

const INTERVALO_MS = 10000;

/**
 * Trae /dashboard/parcelas y la refresca con polling, igual que el panel
 * original (setInterval cada 10s). Se evaluó usar SWR/React Query, pero
 * para una sola fuente de datos sin mutaciones complejas, un hook propio
 * con fetch + setInterval es más simple de leer y no agrega una dependencia
 * extra al proyecto.
 */
export function useParcelas() {
  const [parcelas, setParcelas] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [ultimaActualizacion, setUltimaActualizacion] = useState(null);
  const primerCarga = useRef(true);

  const cargar = useCallback(async () => {
    try {
      const data = await api.getParcelas();
      setParcelas(data.parcelas || []);
      setUltimaActualizacion(new Date());
      setError(null);
    } catch (err) {
      setError(err.message);
    } finally {
      if (primerCarga.current) {
        setLoading(false);
        primerCarga.current = false;
      }
    }
  }, []);

  useEffect(() => {
    cargar();
    const id = setInterval(cargar, INTERVALO_MS);
    return () => clearInterval(id);
  }, [cargar]);

  return { parcelas, loading, error, ultimaActualizacion, refetch: cargar };
}
