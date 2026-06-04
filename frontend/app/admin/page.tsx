'use client'
/**
 * Panel de Administración — CU-07: Configurar campos, parcelas, sensores y reglas.
 */
import { useEffect, useState } from 'react'
import { api, Campo, Parcela, Regla, Sensor, SensorAsignacion } from '@/lib/api'

type Tab = 'campos' | 'parcelas' | 'sensores' | 'reglas'

const FORMULAS = [
  { value: 'humedad_promedio_menor_que', label: 'Humedad promedio < umbral (%)' },
  { value: 'temperatura_menor_que', label: 'Temperatura promedio < umbral (°C) — riesgo helada' },
  { value: 'temperatura_mayor_que', label: 'Temperatura promedio > umbral (°C) — estrés calórico' },
  { value: 'ph_fuera_de_rango', label: '|pH - 7.0| > umbral — anomalía pH' },
]

function BtnDelete({ onClick, label = 'Eliminar' }: { onClick: () => void; label?: string }) {
  return (
    <button
      onClick={onClick}
      className="text-xs text-red-500 hover:text-red-700 hover:underline ml-auto flex-shrink-0"
    >
      {label}
    </button>
  )
}

export default function AdminPage() {
  const [tab, setTab] = useState<Tab>('campos')
  const [campos, setCampos] = useState<Campo[]>([])
  const [parcelas, setParcelas] = useState<Parcela[]>([])
  const [sensores, setSensores] = useState<Sensor[]>([])
  const [asignaciones, setAsignaciones] = useState<SensorAsignacion[]>([])
  const [reglas, setReglas] = useState<Regla[]>([])
  const [msg, setMsg] = useState('')
  const [msgType, setMsgType] = useState<'ok' | 'err'>('ok')

  const flash = (m: string, type: 'ok' | 'err' = 'ok') => {
    setMsg(m); setMsgType(type); setTimeout(() => setMsg(''), 4000)
  }

  const recargar = () => {
    api.campos().then(setCampos).catch(() => {})
    api.parcelas().then(setParcelas).catch(() => {})
    api.reglas().then(setReglas).catch(() => {})
    api.sensores().then(setSensores).catch(() => {})
    api.asignaciones().then(setAsignaciones).catch(() => {})
  }

  useEffect(() => { recargar() }, [])

  // ── Formulario Sensor ─────────────────────────────────────────────────────
  const [fSensor, setFSensor] = useState({ nombre_codigo_sensor: '', estado: 'activo' })
  const crearSensor = async () => {
    if (!fSensor.nombre_codigo_sensor.trim()) return flash('El código del sensor es obligatorio y no puede ser solo espacios.', 'err')
    try {
      await api.crearSensor({ nombre_codigo_sensor: fSensor.nombre_codigo_sensor.trim(), estado: fSensor.estado })
      setFSensor({ nombre_codigo_sensor: '', estado: 'activo' })
      flash(`Sensor "${fSensor.nombre_codigo_sensor}" creado.`)
      api.sensores().then(setSensores).catch(() => {})
    } catch (e: any) { flash(`Error: ${e.message}`, 'err') }
  }

  const eliminarSensor = async (codigo: string) => {
    if (!confirm(`¿Eliminar el sensor "${codigo}"? Se perderán sus asignaciones.`)) return
    try {
      await api.eliminarSensor(codigo)
      flash(`Sensor "${codigo}" eliminado.`)
      api.sensores().then(setSensores).catch(() => {})
      api.asignaciones().then(setAsignaciones).catch(() => {})
    } catch (e: any) { flash(`Error: ${e.message}`, 'err') }
  }

  const [fAsignar, setFAsignar] = useState({ codigo: '', nombre_campo: '', nombre_parcela: '', fecha_instalacion: new Date().toISOString().slice(0, 10) })
  const parcelasFiltradas = parcelas.filter(p => !fAsignar.nombre_campo || p.nombre_campo === fAsignar.nombre_campo)
  const asignarSensor = async () => {
    if (!fAsignar.codigo || !fAsignar.nombre_campo || !fAsignar.nombre_parcela) return flash('Completa todos los campos de asignación.', 'err')
    try {
      await api.asignarSensor(fAsignar.codigo, {
        nombre_parcela: fAsignar.nombre_parcela,
        nombre_campo: fAsignar.nombre_campo,
        fecha_instalacion: new Date(fAsignar.fecha_instalacion).toISOString(),
      })
      flash(`Sensor "${fAsignar.codigo}" asignado a parcela "${fAsignar.nombre_parcela}".`)
      setFAsignar(p => ({ ...p, codigo: '', nombre_parcela: '' }))
      api.asignaciones().then(setAsignaciones).catch(() => {})
    } catch (e: any) { flash(`Error: ${e.message}`, 'err') }
  }

  const desasignarSensor = async (codigo: string, parcela: string) => {
    if (!confirm(`¿Retirar sensor "${codigo}" de "${parcela}"?`)) return
    try {
      await api.desasignarSensor(codigo, parcela)
      flash(`Sensor "${codigo}" retirado de "${parcela}".`)
      api.asignaciones().then(setAsignaciones).catch(() => {})
    } catch (e: any) { flash(`Error: ${e.message}`, 'err') }
  }

  // ── Formulario Campo ──────────────────────────────────────────────────────
  const [fCampo, setFCampo] = useState({ nombre_campo: '', descripcion_campo: '', coordenadas_campo: '' })
  const crearCampo = async () => {
    if (!fCampo.nombre_campo.trim()) return flash('El nombre del campo es obligatorio y no puede ser solo espacios.', 'err')
    try {
      const c = await api.crearCampo({ nombre_campo: fCampo.nombre_campo.trim(), descripcion_campo: fCampo.descripcion_campo, coordenadas_campo: fCampo.coordenadas_campo || undefined })
      setCampos(prev => [...prev, c])
      setFCampo({ nombre_campo: '', descripcion_campo: '', coordenadas_campo: '' })
      flash(`Campo "${c.nombre_campo}" creado.`)
    } catch (e: any) { flash(`Error: ${e.message}`, 'err') }
  }

  const eliminarCampo = async (nombre: string) => {
    if (!confirm(`¿Eliminar el campo "${nombre}"? Esto eliminará también sus parcelas y reglas.`)) return
    try {
      await api.eliminarCampo(nombre)
      flash(`Campo "${nombre}" eliminado.`)
      recargar()
    } catch (e: any) { flash(`Error: ${e.message}`, 'err') }
  }

  // ── Formulario Parcela ────────────────────────────────────────────────────
  const [fParcela, setFParcela] = useState({ nombre_parcela: '', descripcion_parcela: '', nombre_campo: '', coordenadas_parcela: '' })
  const crearParcela = async () => {
    if (!fParcela.nombre_parcela.trim()) return flash('El nombre de la parcela es obligatorio y no puede ser solo espacios.', 'err')
    if (!fParcela.nombre_campo) return flash('Seleccioná el campo al que pertenece la parcela.', 'err')
    try {
      const p = await api.crearParcela({ nombre_parcela: fParcela.nombre_parcela.trim(), descripcion_parcela: fParcela.descripcion_parcela, nombre_campo: fParcela.nombre_campo, coordenadas_parcela: fParcela.coordenadas_parcela || undefined })
      setParcelas(prev => [...prev, p])
      setFParcela({ nombre_parcela: '', descripcion_parcela: '', nombre_campo: '', coordenadas_parcela: '' })
      flash(`Parcela "${p.nombre_parcela}" creada.`)
    } catch (e: any) { flash(`Error: ${e.message}`, 'err') }
  }

  const eliminarParcela = async (nombre: string) => {
    if (!confirm(`¿Eliminar la parcela "${nombre}"?`)) return
    try {
      await api.eliminarParcela(nombre)
      flash(`Parcela "${nombre}" eliminada.`)
      api.parcelas().then(setParcelas).catch(() => {})
      api.asignaciones().then(setAsignaciones).catch(() => {})
    } catch (e: any) { flash(`Error: ${e.message}`, 'err') }
  }

  // ── Formulario Regla ──────────────────────────────────────────────────────
  const [fRegla, setFRegla] = useState({ nombre_regla: '', formula: FORMULAS[0].value, umbral: '', descripcion_regla: '', nombre_campo: '' })
  const crearRegla = async () => {
    try {
      const r = await api.crearRegla({ nombre_regla: fRegla.nombre_regla, formula: fRegla.formula, umbral: parseFloat(fRegla.umbral), descripcion_regla: fRegla.descripcion_regla || undefined, nombre_campo: fRegla.nombre_campo })
      setReglas(prev => [...prev, r])
      setFRegla({ nombre_regla: '', formula: FORMULAS[0].value, umbral: '', descripcion_regla: '', nombre_campo: '' })
      flash(`Regla "${r.nombre_regla}" creada.`)
    } catch (e: any) { flash(`Error: ${e.message}`, 'err') }
  }

  const eliminarRegla = async (nombre: string) => {
    if (!confirm(`¿Eliminar la regla "${nombre}"?`)) return
    try {
      await api.eliminarRegla(nombre)
      flash(`Regla "${nombre}" eliminada.`)
      api.reglas().then(setReglas).catch(() => {})
    } catch (e: any) { flash(`Error: ${e.message}`, 'err') }
  }

  const tabCls = (t: Tab) =>
    `px-4 py-2 text-sm font-medium rounded-t-lg transition-colors ${tab === t ? 'bg-white text-agtech-green border-b-2 border-agtech-green' : 'text-gray-500 hover:text-agtech-green'}`

  return (
    <div className="max-w-5xl mx-auto">
      <h1 className="text-2xl font-bold text-agtech-green mb-2">Panel de Administración</h1>
      <p className="text-gray-500 text-sm mb-6">Gestión de campos, parcelas, sensores y reglas agroclimáticas.</p>

      {msg && (
        <div className={`mb-4 p-3 rounded-lg text-sm ${msgType === 'err' ? 'bg-red-100 text-red-800 border border-red-200' : 'bg-agtech-light text-white'}`}>
          {msg}
        </div>
      )}

      {/* Tabs */}
      <div className="flex gap-1 mb-0 border-b border-gray-200">
        <button className={tabCls('campos')} onClick={() => setTab('campos')}>Campos</button>
        <button className={tabCls('parcelas')} onClick={() => setTab('parcelas')}>Parcelas</button>
        <button className={tabCls('sensores')} onClick={() => setTab('sensores')}>Sensores</button>
        <button className={tabCls('reglas')} onClick={() => setTab('reglas')}>Reglas Agroclimáticas</button>
      </div>

      <div className="bg-white rounded-b-xl rounded-tr-xl shadow p-6">

        {/* TAB CAMPOS */}
        {tab === 'campos' && (
          <div>
            <h2 className="font-semibold text-gray-700 mb-4">Crear nuevo campo</h2>
            <div className="grid md:grid-cols-3 gap-3 mb-4">
              <input className="border rounded-lg px-3 py-2 text-sm" placeholder="Nombre del campo *" value={fCampo.nombre_campo} onChange={e => setFCampo(p => ({ ...p, nombre_campo: e.target.value }))} />
              <input className="border rounded-lg px-3 py-2 text-sm" placeholder="Descripción" value={fCampo.descripcion_campo} onChange={e => setFCampo(p => ({ ...p, descripcion_campo: e.target.value }))} />
              <input className="border rounded-lg px-3 py-2 text-sm" placeholder="Coordenadas GeoJSON (opcional)" value={fCampo.coordenadas_campo} onChange={e => setFCampo(p => ({ ...p, coordenadas_campo: e.target.value }))} />
            </div>
            <button onClick={crearCampo} className="bg-agtech-green text-white px-4 py-2 rounded-lg text-sm hover:bg-agtech-light">+ Crear campo</button>

            <h2 className="font-semibold text-gray-700 mt-8 mb-3">Campos registrados ({campos.length})</h2>
            <div className="grid md:grid-cols-3 gap-3">
              {campos.map(c => (
                <div key={c.nombre_campo} className="border border-agtech-light rounded-lg p-3 flex items-start gap-2">
                  <div className="flex-1 min-w-0">
                    <p className="font-semibold text-agtech-green truncate">{c.nombre_campo}</p>
                    <p className="text-xs text-gray-500">{c.descripcion_campo ?? 'Sin descripción'}</p>
                  </div>
                  <BtnDelete onClick={() => eliminarCampo(c.nombre_campo)} />
                </div>
              ))}
            </div>
          </div>
        )}

        {/* TAB PARCELAS */}
        {tab === 'parcelas' && (
          <div>
            <h2 className="font-semibold text-gray-700 mb-4">Crear nueva parcela</h2>
            <div className="grid md:grid-cols-2 gap-3 mb-4">
              <input className="border rounded-lg px-3 py-2 text-sm" placeholder="Nombre de la parcela *" value={fParcela.nombre_parcela} onChange={e => setFParcela(p => ({ ...p, nombre_parcela: e.target.value }))} />
              <select className="border rounded-lg px-3 py-2 text-sm" value={fParcela.nombre_campo} onChange={e => setFParcela(p => ({ ...p, nombre_campo: e.target.value }))}>
                <option value="">— Campo al que pertenece *</option>
                {campos.map(c => <option key={c.nombre_campo} value={c.nombre_campo}>{c.nombre_campo}</option>)}
              </select>
              <input className="border rounded-lg px-3 py-2 text-sm" placeholder="Descripción" value={fParcela.descripcion_parcela} onChange={e => setFParcela(p => ({ ...p, descripcion_parcela: e.target.value }))} />
              <input className="border rounded-lg px-3 py-2 text-sm" placeholder='GeoJSON — ej: {"type":"Point","coordinates":[-62.3,-38.7]}' value={fParcela.coordenadas_parcela} onChange={e => setFParcela(p => ({ ...p, coordenadas_parcela: e.target.value }))} />
            </div>
            <button onClick={crearParcela} className="bg-agtech-green text-white px-4 py-2 rounded-lg text-sm hover:bg-agtech-light">+ Crear parcela</button>

            <h2 className="font-semibold text-gray-700 mt-8 mb-3">Parcelas registradas ({parcelas.length})</h2>
            <div className="space-y-2">
              {parcelas.map(p => (
                <div key={p.nombre_parcela} className="border border-gray-200 rounded-lg p-3 flex items-center gap-3">
                  <div className="flex-1 min-w-0">
                    <p className="font-semibold text-gray-800">{p.nombre_parcela}</p>
                    <p className="text-xs text-gray-400">
                      Campo: {p.nombre_campo}
                      {p.coordenadas_parcela
                        ? <span className="ml-2 text-green-600">✓ con coordenadas</span>
                        : <span className="ml-2 text-amber-500">⚠ sin coordenadas (no aparece en el mapa)</span>
                      }
                    </p>
                  </div>
                  <BtnDelete onClick={() => eliminarParcela(p.nombre_parcela)} />
                </div>
              ))}
            </div>
          </div>
        )}

        {/* TAB SENSORES */}
        {tab === 'sensores' && (
          <div className="space-y-8">

            {/* Registrar sensor */}
            <div>
              <h2 className="font-semibold text-gray-700 mb-1">Registrar nuevo sensor</h2>
              <p className="text-xs text-gray-400 mb-4">
                El código debe coincidir exactamente con el <strong>DevEUI</strong> que usarás en el LNS Console.
              </p>
              <div className="grid md:grid-cols-3 gap-3">
                <input
                  className="border rounded-lg px-3 py-2 text-sm"
                  placeholder="Código del sensor (ej: SN-001) *"
                  value={fSensor.nombre_codigo_sensor}
                  onChange={e => setFSensor(p => ({ ...p, nombre_codigo_sensor: e.target.value }))}
                />
                <select
                  className="border rounded-lg px-3 py-2 text-sm"
                  value={fSensor.estado}
                  onChange={e => setFSensor(p => ({ ...p, estado: e.target.value }))}
                >
                  <option value="activo">Activo</option>
                  <option value="inactivo">Inactivo</option>
                </select>
                <button onClick={crearSensor} className="bg-agtech-green text-white px-4 py-2 rounded-lg text-sm hover:bg-agtech-light">
                  + Registrar sensor
                </button>
              </div>
            </div>

            {/* Sensores registrados */}
            <div>
              <h2 className="font-semibold text-gray-700 mb-3">Sensores registrados ({sensores.length})</h2>
              {sensores.length === 0 ? (
                <p className="text-sm text-gray-400">No hay sensores registrados aún.</p>
              ) : (
                <div className="grid md:grid-cols-3 gap-3">
                  {sensores.map(s => (
                    <div key={s.nombre_codigo_sensor} className="border border-agtech-light rounded-lg p-3 flex items-center gap-2">
                      <span className={`w-2 h-2 rounded-full flex-shrink-0 ${s.estado === 'activo' ? 'bg-green-500' : 'bg-gray-300'}`} />
                      <div className="flex-1 min-w-0">
                        <p className="font-mono text-sm font-semibold text-agtech-green truncate">{s.nombre_codigo_sensor}</p>
                        <p className="text-xs text-gray-400 capitalize">{s.estado}</p>
                      </div>
                      <BtnDelete onClick={() => eliminarSensor(s.nombre_codigo_sensor)} />
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Asignar sensor */}
            <div>
              <h2 className="font-semibold text-gray-700 mb-1">Asignar sensor a parcela</h2>
              <p className="text-xs text-gray-400 mb-4">
                El sensor debe estar asignado para que el mapa busque sus lecturas en InfluxDB.
              </p>
              <div className="grid md:grid-cols-2 gap-3 mb-3">
                <select
                  className="border rounded-lg px-3 py-2 text-sm"
                  value={fAsignar.codigo}
                  onChange={e => setFAsignar(p => ({ ...p, codigo: e.target.value }))}
                >
                  <option value="">— Sensor *</option>
                  {sensores.map(s => (
                    <option key={s.nombre_codigo_sensor} value={s.nombre_codigo_sensor}>
                      {s.nombre_codigo_sensor} ({s.estado})
                    </option>
                  ))}
                </select>
                <select
                  className="border rounded-lg px-3 py-2 text-sm"
                  value={fAsignar.nombre_campo}
                  onChange={e => setFAsignar(p => ({ ...p, nombre_campo: e.target.value, nombre_parcela: '' }))}
                >
                  <option value="">— Campo *</option>
                  {campos.map(c => <option key={c.nombre_campo} value={c.nombre_campo}>{c.nombre_campo}</option>)}
                </select>
                <select
                  className="border rounded-lg px-3 py-2 text-sm"
                  value={fAsignar.nombre_parcela}
                  onChange={e => setFAsignar(p => ({ ...p, nombre_parcela: e.target.value }))}
                  disabled={!fAsignar.nombre_campo}
                >
                  <option value="">— Parcela *</option>
                  {parcelasFiltradas.map(p => <option key={p.nombre_parcela} value={p.nombre_parcela}>{p.nombre_parcela}</option>)}
                </select>
                <input
                  type="date"
                  className="border rounded-lg px-3 py-2 text-sm"
                  value={fAsignar.fecha_instalacion}
                  onChange={e => setFAsignar(p => ({ ...p, fecha_instalacion: e.target.value }))}
                />
              </div>
              <button onClick={asignarSensor} className="bg-agtech-green text-white px-4 py-2 rounded-lg text-sm hover:bg-agtech-light">
                Asignar sensor
              </button>
            </div>

            {/* Asignaciones activas — verificación */}
            <div>
              <h2 className="font-semibold text-gray-700 mb-1">Asignaciones activas ({asignaciones.length})</h2>
              <p className="text-xs text-gray-400 mb-3">
                Solo los sensores aquí listados enviarán datos al mapa cuando transmitan vía MQTT.
              </p>
              {asignaciones.length === 0 ? (
                <p className="text-sm text-amber-600 bg-amber-50 border border-amber-100 rounded-lg p-3">
                  Ningún sensor está asignado a una parcela. El mapa mostrará datos simulados.
                </p>
              ) : (
                <div className="space-y-2">
                  {asignaciones.map(a => (
                    <div key={`${a.nombre_codigo_sensor}-${a.nombre_parcela}`} className="border border-gray-200 rounded-lg p-3 flex items-center gap-3">
                      <div className="flex-1">
                        <div className="flex items-center gap-2">
                          <span className="font-mono text-sm font-semibold text-agtech-green">{a.nombre_codigo_sensor}</span>
                          <span className="text-gray-400 text-xs">→</span>
                          <span className="text-sm text-gray-700">{a.nombre_parcela}</span>
                          <span className="text-xs bg-gray-100 px-2 py-0.5 rounded text-gray-500">{a.nombre_campo}</span>
                        </div>
                        <p className="text-xs text-gray-400 mt-0.5">
                          Instalado: {new Date(a.fecha_instalacion).toLocaleDateString('es-AR')}
                        </p>
                      </div>
                      <BtnDelete onClick={() => desasignarSensor(a.nombre_codigo_sensor, a.nombre_parcela)} label="Retirar" />
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Guía de flujo */}
            <div className="bg-blue-50 border border-blue-100 rounded-xl p-4 text-xs text-blue-800 space-y-1">
              <p className="font-semibold text-blue-900 mb-2">Flujo para ver datos reales en el mapa</p>
              <p>1. Registrar sensor aquí (código = DevEUI del hardware o del LNS Console)</p>
              <p>2. Asignarlo a una parcela en este mismo tab</p>
              <p>3. LNS Console: campo → gateway → sensor (mismo DevEUI) → iniciar transmisión</p>
              <p>4. El mapa mostrará <strong>origen: Real</strong> en lugar de Simulado</p>
            </div>
          </div>
        )}

        {/* TAB REGLAS */}
        {tab === 'reglas' && (
          <div>
            <h2 className="font-semibold text-gray-700 mb-4">Crear nueva regla agroclimática</h2>
            <div className="grid md:grid-cols-2 gap-3 mb-4">
              <input className="border rounded-lg px-3 py-2 text-sm" placeholder="Nombre de la regla *" value={fRegla.nombre_regla} onChange={e => setFRegla(p => ({ ...p, nombre_regla: e.target.value }))} />
              <select className="border rounded-lg px-3 py-2 text-sm" value={fRegla.nombre_campo} onChange={e => setFRegla(p => ({ ...p, nombre_campo: e.target.value }))}>
                <option value="">— Campo al que aplica *</option>
                {campos.map(c => <option key={c.nombre_campo} value={c.nombre_campo}>{c.nombre_campo}</option>)}
              </select>
              <select className="border rounded-lg px-3 py-2 text-sm" value={fRegla.formula} onChange={e => setFRegla(p => ({ ...p, formula: e.target.value }))}>
                {FORMULAS.map(f => <option key={f.value} value={f.value}>{f.label}</option>)}
              </select>
              <input type="number" className="border rounded-lg px-3 py-2 text-sm" placeholder="Umbral *" value={fRegla.umbral} onChange={e => setFRegla(p => ({ ...p, umbral: e.target.value }))} />
              <input className="border rounded-lg px-3 py-2 text-sm md:col-span-2" placeholder="Descripción de la regla" value={fRegla.descripcion_regla} onChange={e => setFRegla(p => ({ ...p, descripcion_regla: e.target.value }))} />
            </div>
            <button onClick={crearRegla} className="bg-agtech-green text-white px-4 py-2 rounded-lg text-sm hover:bg-agtech-light">+ Crear regla</button>

            <h2 className="font-semibold text-gray-700 mt-8 mb-3">Reglas configuradas ({reglas.length})</h2>
            <div className="space-y-2">
              {reglas.map(r => (
                <div key={r.nombre_regla} className="border border-gray-200 rounded-lg p-3 flex items-start gap-3">
                  <div className="flex-1">
                    <div className="flex items-center gap-3">
                      <p className="font-semibold text-gray-800">{r.nombre_regla}</p>
                      <span className="text-xs bg-gray-100 px-2 py-0.5 rounded text-gray-600">{r.nombre_campo}</span>
                    </div>
                    <p className="text-xs text-gray-500 mt-1">{r.descripcion_regla ?? r.formula} — umbral: <strong>{r.umbral}</strong></p>
                  </div>
                  <BtnDelete onClick={() => eliminarRegla(r.nombre_regla)} />
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
