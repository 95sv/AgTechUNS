'use client'
import { useEffect, useState } from 'react'
import { api, Alerta, Prediccion, Campo } from '@/lib/api'
import { format } from 'date-fns'
import { es } from 'date-fns/locale'

function StatCard({ label, value, sub, color }: { label: string; value: string | number; sub?: string; color?: string }) {
  return (
    <div className={`bg-white rounded-xl shadow p-5 border-l-4 ${color ?? 'border-agtech-green'}`}>
      <p className="text-sm text-gray-500">{label}</p>
      <p className="text-3xl font-bold mt-1">{value}</p>
      {sub && <p className="text-xs text-gray-400 mt-1">{sub}</p>}
    </div>
  )
}

export default function Dashboard() {
  const [campos, setCampos] = useState<Campo[]>([])
  const [alertas, setAlertas] = useState<Alerta[]>([])
  const [predicciones, setPredicciones] = useState<Prediccion[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([api.campos(), api.alertas(10), api.predicciones(5)])
      .then(([c, a, p]) => { setCampos(c); setAlertas(a); setPredicciones(p) })
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <div className="flex justify-center items-center h-64 text-agtech-green font-semibold">Cargando...</div>

  return (
    <div className="max-w-6xl mx-auto">
      <h1 className="text-2xl font-bold text-agtech-green mb-6">Dashboard de Monitoreo</h1>

      {/* KPIs */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        <StatCard label="Campos activos" value={campos.length} color="border-agtech-green" />
        <StatCard label="Alertas recientes" value={alertas.length} color="border-red-400" sub="últimas 10" />
        <StatCard label="Predicciones" value={predicciones.length} color="border-yellow-400" sub="últimas 5" />
        <StatCard label="Sistema" value="Activo" color="border-blue-400" sub="IoT + Analítica" />
      </div>

      <div className="grid md:grid-cols-2 gap-6">
        {/* Alertas recientes */}
        <div className="bg-white rounded-xl shadow p-5">
          <h2 className="font-semibold text-lg mb-4 text-gray-700">Alertas recientes</h2>
          {alertas.length === 0 ? (
            <p className="text-gray-400 text-sm">No hay alertas recientes.</p>
          ) : (
            <ul className="space-y-3">
              {alertas.map(a => (
                <li key={a.id_alerta} className="border-l-4 border-red-400 pl-3 py-1">
                  <p className="text-sm font-medium text-gray-800">{a.nombre_parcela}</p>
                  <p className="text-xs text-gray-500 truncate">{a.mensaje}</p>
                  <p className="text-xs text-gray-400">{format(new Date(a.fecha_emision), 'dd MMM HH:mm', { locale: es })}</p>
                </li>
              ))}
            </ul>
          )}
        </div>

        {/* Predicciones recientes */}
        <div className="bg-white rounded-xl shadow p-5">
          <h2 className="font-semibold text-lg mb-4 text-gray-700">Últimas predicciones del motor analítico</h2>
          {predicciones.length === 0 ? (
            <p className="text-gray-400 text-sm">No hay predicciones generadas aún.</p>
          ) : (
            <ul className="space-y-3">
              {predicciones.map(p => (
                <li key={p.id_prediccion} className="border-l-4 border-yellow-400 pl-3 py-1">
                  <p className="text-sm font-medium text-gray-800">{p.nombre_parcela}</p>
                  <p className="text-xs text-gray-500 truncate">{p.resultado}</p>
                  <p className="text-xs text-gray-400">{format(new Date(p.fecha_emision), 'dd MMM HH:mm', { locale: es })}</p>
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>

      {/* Campos */}
      <div className="bg-white rounded-xl shadow p-5 mt-6">
        <h2 className="font-semibold text-lg mb-4 text-gray-700">Campos registrados</h2>
        {campos.length === 0 ? (
          <p className="text-gray-400 text-sm">No hay campos registrados. Ve a <a href="/admin" className="text-agtech-green underline">Admin</a> para crear uno.</p>
        ) : (
          <div className="grid md:grid-cols-3 gap-4">
            {campos.map(c => (
              <a key={c.nombre_campo} href={`/map?campo=${c.nombre_campo}`} className="block p-4 border border-agtech-light rounded-lg hover:bg-agtech-bg transition-colors">
                <p className="font-semibold text-agtech-green">{c.nombre_campo}</p>
                <p className="text-sm text-gray-500 mt-1">{c.descripcion_campo ?? 'Sin descripción'}</p>
              </a>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
