const ESTILOS_SEVERIDAD = {
  alta: { borde: 'border-red-500', fondo: 'bg-red-50', texto: 'text-red-900', etiqueta: 'text-red-700' },
  media: { borde: 'border-amber-500', fondo: 'bg-amber-50', texto: 'text-amber-900', etiqueta: 'text-amber-700' },
  baja: { borde: 'border-blue-500', fondo: 'bg-blue-50', texto: 'text-blue-900', etiqueta: 'text-blue-700' },
};

export default function AlertaItem({ alerta, nombreParcela }) {
  const estilo = ESTILOS_SEVERIDAD[alerta.severidad] || ESTILOS_SEVERIDAD.baja;

  return (
    <div className={`alerta-item border-l-4 rounded-r-lg p-3 mb-2 ${estilo.borde} ${estilo.fondo}`}>
      <div className="flex items-center justify-between mb-1">
        <span className={`font-medium text-sm ${estilo.texto}`}>{alerta.tipo.replaceAll('_', ' ')}</span>
        <span className={`text-xs uppercase tracking-wider font-semibold ${estilo.etiqueta}`}>
          {alerta.severidad}
        </span>
      </div>
      <p className="text-xs text-stone-700">{alerta.mensaje}</p>
      <p className="text-xs text-stone-500 mt-1">{nombreParcela}</p>
    </div>
  );
}
