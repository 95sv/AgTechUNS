'use client';
import { useRef } from 'react';
import { useGSAP, gsap } from '@/lib/gsapSetup';
import AlertaItem from './AlertaItem';

export default function AnalyticsPanel({ resultado }) {
  const containerRef = useRef(null);

  useGSAP(
    () => {
      if (!resultado) return;
      gsap.from('.alerta-item', {
        opacity: 0,
        x: -16,
        duration: 0.4,
        stagger: 0.06,
        ease: 'power2.out',
      });
    },
    { dependencies: [resultado], scope: containerRef }
  );

  if (!resultado) return null;

  const alertas = (resultado.detalle ?? []).flatMap((d) =>
    d.alertas_generadas.map((a) => ({ ...a, nombreParcela: d.nombre_parcela }))
  );

  return (
    <section ref={containerRef} className="bg-white rounded-2xl border border-stone-200 p-5 shadow-sm">
      <div className="flex items-center justify-between mb-3">
        <h2 className="text-lg font-semibold text-stone-900">Resultado del análisis</h2>
        <span className="text-xs text-stone-500">{resultado.total_alertas ?? 0} alertas</span>
      </div>

      {alertas.length === 0 ? (
        <p className="text-sm text-stone-500 italic">Sin condiciones críticas detectadas.</p>
      ) : (
        alertas.map((alerta, i) => (
          <AlertaItem key={`${alerta.tipo}-${alerta.nombreParcela}-${i}`} alerta={alerta} nombreParcela={alerta.nombreParcela} />
        ))
      )}
    </section>
  );
}
