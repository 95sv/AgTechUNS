export default function ParcelaCard({ parcela }) {
  const humedad = parcela.ultima_lectura?.valor_humedad;
  const temperatura = parcela.ultima_lectura?.valor_temperatura;
  const climaAmbiente = parcela.clima_actual?.temperature;

  return (
    <div className="parcela-card bg-white rounded-2xl border border-stone-200 p-5 shadow-sm">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <div className={`w-2 h-2 rounded-full ${parcela.ultima_lectura ? 'bg-emerald-500' : 'bg-stone-300'}`} />
          <h3 className="font-semibold text-stone-900">{parcela.nombre_parcela}</h3>
        </div>
        <span className="text-xs text-stone-400">{parcela.nombre_codigo_sensor}</span>
      </div>

      <div className="grid grid-cols-2 gap-3 mb-4">
        <div className="bg-blue-50 rounded-lg p-3">
          <div className="text-xs text-blue-700 font-medium uppercase tracking-wide">Humedad suelo</div>
          <div className="text-2xl font-bold text-blue-900 mt-1">
            {humedad?.toFixed(1) ?? '—'} <span className="text-base font-normal text-blue-600">%</span>
          </div>
        </div>
        <div className="bg-orange-50 rounded-lg p-3">
          <div className="text-xs text-orange-700 font-medium uppercase tracking-wide">Temp. sensor</div>
          <div className="text-2xl font-bold text-orange-900 mt-1">
            {temperatura?.toFixed(1) ?? '—'} <span className="text-base font-normal text-orange-600">°C</span>
          </div>
        </div>
      </div>

      <div className="border-t border-stone-100 pt-3 flex items-center justify-between text-sm">
        <span className="text-stone-500">🌤️ Clima ambiente</span>
        <span className="font-medium text-stone-900">
          {climaAmbiente ?? '—'} <span className="text-stone-500">°C</span>
        </span>
      </div>
    </div>
  );
}
