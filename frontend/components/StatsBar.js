'use client';
import StatNumber from './StatNumber';

export default function StatsBar({ totalParcelas, enLinea, totalAlertas }) {
  const items = [
    { label: 'Parcelas totales', value: totalParcelas, color: 'text-stone-900' },
    { label: 'En línea', value: enLinea, color: 'text-emerald-700' },
    { label: 'Alertas activas', value: totalAlertas, color: totalAlertas > 0 ? 'text-red-600' : 'text-stone-900' },
  ];

  return (
    <div className="grid grid-cols-3 gap-4">
      {items.map((it) => (
        <div key={it.label} className="bg-white rounded-2xl border border-stone-200 p-4 shadow-sm text-center">
          <div className={`text-3xl font-bold ${it.color}`}>
            <StatNumber value={it.value} />
          </div>
          <div className="text-xs text-stone-500 mt-1 uppercase tracking-wide">{it.label}</div>
        </div>
      ))}
    </div>
  );
}
