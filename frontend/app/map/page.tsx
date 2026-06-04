'use client'

import { Fragment, useEffect, useState, useCallback, Suspense } from 'react'
import { useSearchParams } from 'next/navigation'
import { api, MapaCampo, ParcelaMapa } from '@/lib/api'

// Leaflet se importa condicionalmente (no funciona en SSR)
let MapContainer: any, TileLayer: any, Polygon: any, Popup: any, CircleMarker: any, useMap: any
if (typeof window !== 'undefined') {
  const leaflet = require('react-leaflet')
  MapContainer = leaflet.MapContainer
  TileLayer = leaflet.TileLayer
  Polygon = leaflet.Polygon
  Popup = leaflet.Popup
  CircleMarker = leaflet.CircleMarker
  useMap = leaflet.useMap
}

function SensorInfo({ sensores }: { sensores: Record<string, any> }) {
  const entries = Object.entries(sensores)
  if (entries.length === 0) return <p className="text-xs text-gray-400">Sin datos de sensores recientes</p>
  return (
    <div className="space-y-1">
      {entries.map(([id, l]) => (
        <div key={id} className="text-xs">
          <span className="font-medium">{id}:</span>{' '}
          {l.temperatura != null && <span>🌡 {l.temperatura.toFixed(1)}°C</span>}{' '}
          {l.humedad != null && <span>💧 {l.humedad.toFixed(1)}%</span>}{' '}
          {l.ph != null && <span>⚗ pH {l.ph.toFixed(1)}</span>}
        </div>
      ))}
    </div>
  )
}

function NdviBar({ value, label }: { value?: number; label: string }) {
  if (value == null) return <span className="text-xs text-gray-400">{label}: N/D</span>
  const pct = Math.round(((value + 1) / 2) * 100)
  const color = value > 0.5 ? 'bg-green-500' : value > 0.2 ? 'bg-yellow-400' : 'bg-red-400'
  return (
    <div className="text-xs mt-1">
      <span className="font-medium">{label}: {value.toFixed(3)}</span>
      <div className="w-full bg-gray-200 rounded h-1.5 mt-0.5">
        <div className={`${color} h-1.5 rounded`} style={{ width: `${pct}%` }} />
      </div>
    </div>
  )
}

function WeatherInfo({ clima }: { clima?: MapaCampo['parcelas'][number]['clima'] }) {
  const pronostico = clima?.pronostico?.[0]
  if (!clima || !pronostico) return <p className="text-xs text-gray-400">Sin pronóstico disponible</p>
  return (
    <div className="text-xs space-y-1">
      <p className="font-medium">{clima.fuente}</p>
      <p>🌡 Máx {pronostico.temperatura_max ?? 'N/D'}°C · Mín {pronostico.temperatura_min ?? 'N/D'}°C</p>
      <p>🌧 Lluvia estimada {pronostico.precipitacion_mm ?? 'N/D'} mm</p>
      <p className="text-gray-500">{pronostico.fecha}</p>
    </div>
  )
}

function RulesInfo({ reglas }: { reglas: MapaCampo['reglas'] }) {
  if (!reglas?.length) return <p className="text-xs text-gray-400">Sin reglas configuradas para este campo</p>
  return (
    <div className="space-y-1">
      {reglas.map(r => (
        <div key={r.nombre_regla} className="text-xs rounded-lg bg-amber-50 border border-amber-100 px-2 py-1">
          <p className="font-medium text-amber-900">{r.nombre_regla}</p>
          <p className="text-amber-800">{r.descripcion_regla ?? r.formula}</p>
          <p className="text-amber-700">Umbral: {r.umbral}</p>
        </div>
      ))}
    </div>
  )
}

function MapPopupCard({ parcela, reglas }: { parcela: ParcelaMapa; reglas: MapaCampo['reglas'] }) {
  const { temperatura_promedio, humedad_promedio, ph_promedio } = parcela.sensores_resumen ?? {}
  const origenSensores = parcela.sensores_origen === 'simulado' ? 'Simulados' : parcela.sensores_origen === 'real' ? 'Reales' : 'Mixtos'

  return (
    <div className="text-sm space-y-3 min-w-[260px] max-w-[320px]">
      <div>
        <p className="font-bold text-slate-900">{parcela.parcela}</p>
        <p className="text-gray-500 text-xs">{parcela.descripcion}</p>
      </div>

      <div>
        <p className="text-xs font-semibold uppercase tracking-wide text-slate-500 mb-1">Lecturas registradas</p>
        <p className="text-[11px] uppercase tracking-wide text-blue-600 mb-1">Origen: {origenSensores}</p>
        <div className="text-xs space-y-1">
          <p>🌡 Temperatura promedio: {temperatura_promedio ?? 'N/D'}°C</p>
          <p>💧 Humedad promedio: {humedad_promedio ?? 'N/D'}%</p>
          <p>⚗ pH promedio: {ph_promedio ?? 'N/D'}</p>
        </div>
        <div className="mt-2">
          <SensorInfo sensores={parcela.sensores} />
        </div>
      </div>

      <div>
        <p className="text-xs font-semibold uppercase tracking-wide text-slate-500 mb-1">Clima ambiente</p>
        <WeatherInfo clima={parcela.clima ?? undefined} />
      </div>

      <div>
        <p className="text-xs font-semibold uppercase tracking-wide text-slate-500 mb-1">Reglas del campo</p>
        <RulesInfo reglas={reglas} />
      </div>

      <div>
        <p className="text-xs text-gray-500">NDVI: {parcela.satelital.ndvi ?? 'N/D'} · NDMI: {parcela.satelital.ndmi ?? 'N/D'}</p>
        {parcela.centro && (
          <p className="text-xs text-gray-400 mt-1">
            Centro: {parcela.centro.lat.toFixed(5)}, {parcela.centro.lon.toFixed(5)}
          </p>
        )}
      </div>
    </div>
  )
}

function MapBoundsUpdater({ parcelas }: { parcelas: ParcelaMapa[] }) {
  const map = useMap()

  useEffect(() => {
    if (!map || !parcelas.length) return

    const points: [number, number][] = []

    parcelas.forEach(parcela => {
      if (parcela.coordenadas && (parcela.coordenadas as any).type === 'Polygon') {
        const coords = ((parcela.coordenadas as any).coordinates?.[0] ?? []) as number[][]
        coords.forEach(([lng, lat]) => points.push([lat, lng]))
      } else if (parcela.centro) {
        points.push([parcela.centro.lat, parcela.centro.lon])
      }
    })

    if (points.length === 0) return
    if (points.length === 1) {
      map.setView(points[0], 16)
      return
    }

    map.fitBounds(points)
  }, [map, parcelas])

  return null
}

function ParcelMarker({ parcela, reglas }: { parcela: ParcelaMapa; reglas: MapaCampo['reglas'] }) {
  if (!parcela.centro) return null

  return (
    <CircleMarker
      center={[parcela.centro.lat, parcela.centro.lon]}
      radius={9}
      pathOptions={{ color: '#1d4ed8', fillColor: '#60a5fa', fillOpacity: 0.95, weight: 2 }}
    >
      <Popup>
        <MapPopupCard parcela={parcela} reglas={reglas} />
      </Popup>
    </CircleMarker>
  )
}

function MapContent() {
  const params = useSearchParams()
  const campoParam = params?.get('campo') ?? ''
  const [campos, setCampos] = useState<string[]>([])
  const [campoPicked, setCampoPicked] = useState(campoParam)
  const [mapa, setMapa] = useState<MapaCampo | null>(null)
  const [loading, setLoading] = useState(false)
  const [mounted, setMounted] = useState(false)

  useEffect(() => { setMounted(true) }, [])

  useEffect(() => {
    api.campos().then(cs => setCampos(cs.map(c => c.nombre_campo))).catch(() => {})
  }, [])

  const cargarMapa = useCallback(async (nombre: string) => {
    if (!nombre) return
    setLoading(true)
    try {
      const data = await api.mapaCampo(nombre)
      setMapa(data)
    } catch { setMapa(null) }
    setLoading(false)
  }, [])

  useEffect(() => { if (campoPicked) cargarMapa(campoPicked) }, [campoPicked, cargarMapa])

  // Centra el mapa en Bahía Blanca como default
  const center: [number, number] = [-38.7, -62.3]

  return (
    <div className="max-w-6xl mx-auto">
      <div className="flex items-center gap-4 mb-4">
        <h1 className="text-2xl font-bold text-agtech-green">Mapa de Parcelas</h1>
        <select
          value={campoPicked}
          onChange={e => setCampoPicked(e.target.value)}
          className="border border-agtech-light rounded px-3 py-1.5 text-sm"
        >
          <option value="">— Seleccionar campo —</option>
          {campos.map(c => <option key={c} value={c}>{c}</option>)}
        </select>
        {campoPicked && (
          <button
            onClick={() => cargarMapa(campoPicked)}
            className="bg-agtech-green text-white px-3 py-1.5 rounded text-sm hover:bg-agtech-light transition-colors"
          >
            Actualizar
          </button>
        )}
      </div>

      {!campoPicked && (
        <p className="text-gray-500 text-sm mb-4">Selecciona un campo para visualizar sus parcelas y datos de sensores.</p>
      )}

      <div className="grid md:grid-cols-3 gap-4">
        {/* Mapa */}
        <div className="md:col-span-2 bg-white rounded-xl shadow overflow-hidden" style={{ height: 500 }}>
          {mounted && MapContainer ? (
            <MapContainer center={center} zoom={12} style={{ height: '100%', width: '100%' }}>
              <TileLayer
                attribution='© <a href="https://www.openstreetmap.org/">OpenStreetMap</a>'
                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
              />
              <MapBoundsUpdater parcelas={mapa?.parcelas ?? []} />
              {mapa?.parcelas.map(p => {
                if (!p.coordenadas || (p.coordenadas as any).type !== 'Polygon') return null
                const positions = ((p.coordenadas as any).coordinates[0] as number[][]).map(
                  ([lng, lat]) => [lat, lng] as [number, number]
                )
                const ndvi = p.satelital.ndvi ?? 0
                const color = ndvi > 0.5 ? '#2d6a4f' : ndvi > 0.2 ? '#d4a017' : '#ef4444'
                return (
                  <Fragment key={p.parcela}>
                    <Polygon key={p.parcela} positions={positions} pathOptions={{ color, fillOpacity: 0.4 }} />
                    <ParcelMarker key={`${p.parcela}-marker`} parcela={p} reglas={mapa.reglas} />
                  </Fragment>
                )
              })}
            </MapContainer>
          ) : (
            <div className="flex items-center justify-center h-full text-gray-400">
              {loading ? 'Cargando mapa...' : 'Selecciona un campo'}
            </div>
          )}
        </div>

        {/* Panel lateral */}
        <div className="space-y-3 overflow-y-auto max-h-[500px]">
          {mapa ? mapa.parcelas.map(p => (
            <div key={p.parcela} className="bg-white rounded-xl shadow p-4">
              <p className="font-semibold text-agtech-green">{p.parcela}</p>
              <p className="text-xs text-gray-400 mb-2">{p.descripcion}</p>
              <SensorInfo sensores={p.sensores} />
              <div className="mt-2 text-xs space-y-1 text-gray-700">
                <p>🌡 Temperatura promedio: {p.sensores_resumen?.temperatura_promedio ?? 'N/D'}°C</p>
                <p>💧 Humedad promedio: {p.sensores_resumen?.humedad_promedio ?? 'N/D'}%</p>
              </div>
              <div className="mt-2 text-xs text-gray-500">
                <p>Clima: {p.clima?.pronostico?.[0]?.temperatura_max ?? 'N/D'}°C / {p.clima?.pronostico?.[0]?.temperatura_min ?? 'N/D'}°C</p>
                <p>Lluvia: {p.clima?.pronostico?.[0]?.precipitacion_mm ?? 'N/D'} mm</p>
              </div>
              <div className="mt-2 pt-2 border-t border-gray-100">
                <NdviBar value={p.satelital.ndvi} label="NDVI" />
                <NdviBar value={p.satelital.ndmi} label="NDMI" />
              </div>
            </div>
          )) : (
            <div className="bg-white rounded-xl shadow p-4 text-gray-400 text-sm">
              {campoPicked ? 'Cargando datos...' : 'Selecciona un campo para ver las parcelas.'}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default function MapPage() {
  return (
    <Suspense fallback={<div className="flex items-center justify-center h-64 text-gray-400">Cargando mapa...</div>}>
      <MapContent />
    </Suspense>
  )
}
