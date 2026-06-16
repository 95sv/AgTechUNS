'use client';
import { useEffect, useRef, useState } from 'react';
import Link from 'next/link';
import AuthGuard from '@/components/AuthGuard';
import { useGSAP, gsap } from '@/lib/gsapSetup';
import { api } from '@/lib/api';

function EstadoBadge({ ok }) {
  return (
    <span
      className={`text-xs font-semibold uppercase tracking-wide px-2 py-1 rounded-full ${
        ok ? 'bg-emerald-100 text-emerald-700' : 'bg-red-100 text-red-700'
      }`}
    >
      {ok ? 'OK' : 'Caído'}
    </span>
  );
}

function DiagnosticoContent() {
  const [health, setHealth] = useState(null);
  const [integracion, setIntegracion] = useState(null);
  const [cargando, setCargando] = useState(true);
  const containerRef = useRef(null);

  async function cargar() {
    setCargando(true);
    const [h, i] = await Promise.allSettled([api.getHealth(), api.getIntegracion()]);
    setHealth(h.status === 'fulfilled' ? h.value : null);
    setIntegracion(i.status === 'fulfilled' ? i.value : null);
    setCargando(false);
  }

  useEffect(() => {
    cargar();
  }, []);

  useGSAP(
    () => {
      if (cargando) return;
      gsap.from('.diag-card', { opacity: 0, y: 16, duration: 0.4, stagger: 0.1, ease: 'power2.out' });
    },
    { dependencies: [cargando], scope: containerRef }
  );

  return (
    <main className="max-w-4xl mx-auto px-6 py-10" ref={containerRef}>
      <div className="flex items-center justify-between mb-6">
        <div>
          <Link href="/dashboard" className="text-xs text-stone-500 hover:text-emerald-700">
            ← Volver al panel
          </Link>
          <h1 className="text-2xl font-semibold text-stone-900 mt-1">Diagnóstico del sistema</h1>
          <p className="text-sm text-stone-500">
            Verifica que el backend esté conectado a sus dos fuentes de datos: InfluxDB y el External Data Gateway.
          </p>
        </div>
        <button
          onClick={cargar}
          className="px-4 py-2 bg-stone-100 hover:bg-stone-200 text-sm font-medium rounded-lg transition"
        >
          ↻ Reintentar
        </button>
      </div>

      {cargando ? (
        <p className="text-sm text-stone-400">Consultando backend…</p>
      ) : (
        <div className="space-y-4">
          <div className="diag-card bg-white rounded-2xl border border-stone-200 p-5 shadow-sm flex items-center justify-between">
            <div>
              <h2 className="font-semibold text-stone-900">Backend principal (FastAPI)</h2>
              <p className="text-xs text-stone-500">{health?.service ?? 'sin respuesta'}</p>
            </div>
            <EstadoBadge ok={!!health} />
          </div>

          <div className="diag-card bg-white rounded-2xl border border-stone-200 p-5 shadow-sm">
            <div className="flex items-center justify-between mb-2">
              <h2 className="font-semibold text-stone-900">InfluxDB (lecturas de sensores)</h2>
              <EstadoBadge ok={!!integracion?.influxdb?.ok} />
            </div>
            {integracion?.influxdb?.ok ? (
              <p className="text-xs text-stone-500">
                Sensor consultado: {integracion.influxdb.sensor_consultado}
              </p>
            ) : (
              <p className="text-xs text-red-600">{integracion?.influxdb?.error ?? 'Sin datos'}</p>
            )}
          </div>

          <div className="diag-card bg-white rounded-2xl border border-stone-200 p-5 shadow-sm">
            <div className="flex items-center justify-between mb-2">
              <h2 className="font-semibold text-stone-900">External Data Gateway (clima)</h2>
              <EstadoBadge ok={!!integracion?.external_gateway?.ok} />
            </div>
            {integracion?.external_gateway?.ok ? (
              <p className="text-xs text-stone-500">
                Temperatura ambiente: {integracion.external_gateway.clima_actual?.temperature}°C
              </p>
            ) : (
              <p className="text-xs text-red-600">{integracion?.external_gateway?.error ?? 'Sin datos'}</p>
            )}
          </div>

          <div
            className={`diag-card rounded-2xl border p-5 shadow-sm text-center font-medium ${
              integracion?.stack_ok
                ? 'bg-emerald-50 border-emerald-200 text-emerald-700'
                : 'bg-amber-50 border-amber-200 text-amber-700'
            }`}
          >
            {integracion?.stack_ok ? '✅ Stack completo operativo' : '⚠️ Hay al menos una fuente caída'}
          </div>
        </div>
      )}
    </main>
  );
}

export default function DiagnosticoPage() {
  return <AuthGuard>{() => <DiagnosticoContent />}</AuthGuard>;
}
