'use client';
import { useEffect, useRef, useState } from 'react';
import dynamic from 'next/dynamic';
import AuthGuard from '@/components/AuthGuard';
import Header from '@/components/Header';
import StatsBar from '@/components/StatsBar';
import ParcelasGrid from '@/components/ParcelasGrid';
import AnalyticsPanel from '@/components/AnalyticsPanel';
import { useParcelas } from '@/hooks/useParcelas';
import { api } from '@/lib/api';

// Leaflet necesita `window`: se carga solo en el cliente, nunca en el render
// de servidor de Next (de lo contrario el build falla con "window is not defined").
const MapaParcelas = dynamic(() => import('@/components/MapaParcelas'), {
  ssr: false,
  loading: () => (
    <div className="h-full min-h-[500px] rounded-2xl bg-stone-100 animate-pulse" />
  ),
});

function DashboardContent() {
  const { parcelas, error: errorParcelas } = useParcelas();
  const [seleccionadas, setSeleccionadas] = useState([]);
  const [evaluando, setEvaluando] = useState(false);
  const [resultadoAnalytics, setResultadoAnalytics] = useState(null);
  const [errorAnalytics, setErrorAnalytics] = useState(null);
  const nombresPrevios = useRef([]);

  // Misma lógica del panel original: en la primera carga seleccionar todas;
  // si aparece una parcela nueva más adelante, sumarla a la selección activa.
  useEffect(() => {
    if (parcelas.length === 0) return;
    const nombresActuales = parcelas.map((p) => p.nombre_parcela);
    if (nombresPrevios.current.length === 0) {
      setSeleccionadas(nombresActuales);
    } else {
      const nuevas = nombresActuales.filter((n) => !nombresPrevios.current.includes(n));
      if (nuevas.length > 0) setSeleccionadas((prev) => [...prev, ...nuevas]);
    }
    nombresPrevios.current = nombresActuales;
  }, [parcelas]);

  async function evaluarAnalytics() {
    setEvaluando(true);
    setErrorAnalytics(null);
    try {
      // Llama al endpoint del contrato YAML: GET /campos/{campo}/parcelas/{parcela}/recomendaciones
      const resultados = await Promise.all(
        visibles.map((p) => api.getRecomendaciones(p.nombre_campo, p.nombre_parcela))
      );
      const todasLasAlertas = resultados.flatMap((r) => r.data || []);
      setResultadoAnalytics({
        total_alertas: todasLasAlertas.length,
        detalle: todasLasAlertas,
      });
    } catch (err) {
      setErrorAnalytics(err.message);
    } finally {
      setEvaluando(false);
    }
  }

  const visibles = parcelas.filter((p) => seleccionadas.includes(p.nombre_parcela));
  const enLinea = parcelas.filter((p) => p.ultima_lectura).length;

  return (
    <AuthGuard>
      {(usuario) => (
        <>
          <Header
            parcelas={parcelas}
            seleccionadas={seleccionadas}
            onChangeSeleccion={setSeleccionadas}
            onEvaluar={evaluarAnalytics}
            evaluando={evaluando}
            usuario={usuario}
          />

          <main className="max-w-7xl mx-auto px-6 py-6 space-y-6">
            {errorParcelas && (
              <div className="bg-red-50 border border-red-200 text-red-700 text-sm rounded-xl px-4 py-3">
                {errorParcelas}
              </div>
            )}

            <StatsBar totalParcelas={parcelas.length} enLinea={enLinea} totalAlertas={resultadoAnalytics?.total_alertas ?? 0} />

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <section className="lg:col-span-2 bg-white rounded-2xl border border-stone-200 p-4 shadow-sm">
                <div className="flex items-center justify-between mb-3 px-2">
                  <h2 className="text-lg font-semibold text-stone-900">Mapa de parcelas</h2>
                  <span className="text-xs text-stone-500">{visibles.length} visible(s)</span>
                </div>
                <MapaParcelas parcelas={visibles} />
              </section>

              <aside className="space-y-6">
                <section className="space-y-4">
                  <h2 className="text-lg font-semibold text-stone-900 px-1">Parcelas en línea</h2>
                  <ParcelasGrid parcelas={visibles} />
                </section>

                {errorAnalytics && (
                  <div className="bg-red-50 border border-red-200 text-red-700 text-sm rounded-xl px-4 py-3">
                    {errorAnalytics}
                  </div>
                )}
                <AnalyticsPanel resultado={resultadoAnalytics} />
              </aside>
            </div>
          </main>

          <footer className="max-w-7xl mx-auto px-6 py-4 text-xs text-stone-400 text-center">
            Sensores simulados · Datos meteorológicos: Open-Meteo via External Data Gateway
          </footer>
        </>
      )}
    </AuthGuard>
  );
}

export default function DashboardPage() {
  return <DashboardContent />;
}
