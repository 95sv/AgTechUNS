'use client'
/**
 * CU-02: Consultar recomendaciones agronómicas.
 * Lista predicciones generadas por el Analytics Engine, ordenadas por criticidad.
 */
import { useEffect, useState } from 'react'
import { api, Prediccion } from '@/lib/api'
import { format } from 'date-fns'
import { es } from 'date-fns/locale'

function RiesgoTag({ resultado }: { resultado: string }) {
  const lower = resultado.toLowerCase()
  if (lower.includes('helada') || lower.includes('temperatura')) {
    return <span className="bg-blue-100 text-blue-700 text-xs px-2 py-0.5 rounded font-semibold">Riesgo Helada</span>
  }
  if (lower.includes('humedad') || lower.includes('estrés hídrico') || lower.includes('riego')) {
    return <span className="bg-orange-100 text-orange-700 text-xs px-2 py-0.5 rounded font-semibold">Estrés Hídrico</span>
  }
  if (lower.includes('ph')) {
    return <span className="bg-purple-100 text-purple-700 text-xs px-2 py-0.5 rounded font-semibold">Anomalía pH</span>
  }
  return <span className="bg-gray-100 text-gray-600 text-xs px-2 py-0.5 rounded font-semibold">Alerta General</span>
}

export default function RecommendationsPage() {
  const [predicciones, setPredicciones] = useState<Prediccion[]>([])
  const [loading, setLoading] = useState(true)
  const [ejecutando, setEjecutando] = useState(false)
  const [detalle, setDetalle] = useState<Prediccion | null>(null)

  const cargar = () => {
    setLoading(true)
    api.predicciones(50).then(setPredicciones).catch(() => {}).finally(() => setLoading(false))
  }

  useEffect(() => { cargar() }, [])

  const ejecutarBatch = async () => {
    setEjecutando(true)
    try {
      await api.ejecutarBatch()
      await new Promise(r => setTimeout(r, 2000))
      cargar()
    } catch {}
    setEjecutando(false)
  }

  return (
    <div className="max-w-4xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-agtech-green">Recomendaciones Agronómicas</h1>
        <button
          onClick={ejecutarBatch}
          disabled={ejecutando}
          className="bg-agtech-green text-white px-4 py-2 rounded-lg text-sm hover:bg-agtech-light transition-colors disabled:opacity-60"
        >
          {ejecutando ? 'Ejecutando análisis...' : 'Ejecutar análisis ahora'}
        </button>
      </div>

      {loading ? (
        <p className="text-gray-400 text-center py-12">Cargando recomendaciones...</p>
      ) : predicciones.length === 0 ? (
        <div className="bg-white rounded-xl shadow p-8 text-center text-gray-400">
          <p className="text-4xl mb-3">🌿</p>
          <p className="text-lg font-semibold">No hay nuevas recomendaciones por el momento.</p>
          <p className="text-sm mt-1">Sus parcelas presentan condiciones óptimas según el último análisis.</p>
        </div>
      ) : (
        <div className="space-y-3">
          {predicciones.map(p => (
            <div
              key={p.id_prediccion}
              onClick={() => setDetalle(detalle?.id_prediccion === p.id_prediccion ? null : p)}
              className="bg-white rounded-xl shadow p-5 border-l-4 border-yellow-400 cursor-pointer hover:bg-yellow-50 transition-colors"
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="font-semibold text-gray-800">{p.nombre_parcela}</span>
                    <RiesgoTag resultado={p.resultado} />
                  </div>
                  <p className="text-sm text-gray-600 truncate">{p.resultado}</p>
                </div>
                <p className="text-xs text-gray-400 whitespace-nowrap ml-4">
                  {format(new Date(p.fecha_emision), 'dd MMM HH:mm', { locale: es })}
                </p>
              </div>

              {detalle?.id_prediccion === p.id_prediccion && (
                <div className="mt-4 pt-4 border-t border-gray-100">
                  <p className="text-sm text-gray-700"><span className="font-semibold">Motivo:</span> {p.resultado}</p>
                  <p className="text-xs text-gray-400 mt-2">
                    Período analizado: {format(new Date(p.fecha_ini), 'dd/MM HH:mm', { locale: es })} →{' '}
                    {format(new Date(p.fecha_fin), 'dd/MM HH:mm', { locale: es })}
                  </p>
                  <p className="text-sm text-agtech-green font-semibold mt-3">
                    Acción sugerida: Verificar condiciones de campo y tomar medidas preventivas.
                  </p>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
