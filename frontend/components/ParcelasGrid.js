'use client';
import { useRef } from 'react';
import { useGSAP, gsap } from '@/lib/gsapSetup';
import ParcelaCard from './ParcelaCard';

/** Grilla de tarjetas con stagger de entrada cada vez que cambia la selección visible. */
export default function ParcelasGrid({ parcelas }) {
  const containerRef = useRef(null);
  const claveVisible = parcelas.map((p) => p.nombre_parcela).join(',');

  useGSAP(
    () => {
      gsap.from('.parcela-card', {
        opacity: 0,
        y: 16,
        duration: 0.45,
        stagger: 0.08,
        ease: 'power2.out',
      });
    },
    { dependencies: [claveVisible], scope: containerRef }
  );

  if (parcelas.length === 0) {
    return (
      <div className="bg-white rounded-2xl border border-dashed border-stone-300 p-8 text-center">
        <p className="text-sm text-stone-500">Sin parcelas seleccionadas. Abrí el filtro para elegir cuáles ver.</p>
      </div>
    );
  }

  return (
    <div ref={containerRef} className="space-y-4">
      {parcelas.map((p) => (
        <ParcelaCard key={p.nombre_parcela} parcela={p} />
      ))}
    </div>
  );
}
