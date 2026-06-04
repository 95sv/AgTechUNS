'use client'
import { useEffect, useState } from 'react'
import { api, Alerta } from '@/lib/api'
import { format } from 'date-fns'
import { es } from 'date-fns/locale'

export default function AlertsPage() {
  const [alertas, setAlertas] = useState<Alerta[]>([])
  const [loading, setLoading] = useState(true)

  const cargar = () => {
    setLoading(true)
    api.alertas(100).then(setAlertas).catch(() => {}).finally(() => setLoading(false))
  }

  useEffect(() => { cargar() }, [])

  return (
    <div className="max-w-4xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-agtech-green">Alertas del Sistema</h1>
        <button onClick={cargar} className="bg-agtech-green text-white px-4 py-2 rounded-lg text-sm hover:bg-agtech-light transition-colors">
          Actualizar
        </button>
      </div>

      {loading ? (
        <p className="text-gray-400 text-center py-12">Cargando alertas...</p>
      ) : alertas.length === 0 ? (
        <div className="bg-white rounded-xl shadow p-8 text-center text-gray-400">
          <p className="text-4xl mb-3">✅</p>
          <p className="text-lg font-semibold">No hay alertas activas</p>
          <p className="text-sm mt-1">Sus parcelas presentan condiciones óptimas según el último análisis.</p>
        </div>
      ) : (
        <div className="space-y-3">
          {alertas.map(a => (
            <div key={a.id_alerta} className="bg-white rounded-xl shadow p-5 border-l-4 border-red-400">
              <div className="flex items-start justify-between">
                <div>
                  <span className="inline-block bg-red-100 text-red-700 text-xs font-semibold px-2 py-0.5 rounded mb-2">
                    {a.nombre_parcela}
                  </span>
                  <p className="text-sm text-gray-700">{a.mensaje}</p>
                </div>
                <p className="text-xs text-gray-400 whitespace-nowrap ml-4">
                  {format(new Date(a.fecha_emision), 'dd MMM yyyy HH:mm', { locale: es })}
                </p>
              </div>
              <p className="text-xs text-gray-400 mt-2">Notificado a: {a.email_usuario}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
