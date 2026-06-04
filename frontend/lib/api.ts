const API = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000'

function getToken(): string | null {
  if (typeof window === 'undefined') return null
  return localStorage.getItem('agtech_token')
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const token = getToken()
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...options.headers,
  }
  const res = await fetch(`${API}${path}`, { ...options, headers })
  if (res.status === 401) {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('agtech_token')
      localStorage.removeItem('agtech_email')
      window.location.href = '/login'
    }
    throw new Error('No autenticado')
  }
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(err.detail ?? 'Error en la API')
  }
  if (res.status === 204 || res.headers.get('content-length') === '0') {
    return undefined as T
  }
  return res.json() as Promise<T>
}

async function proxyRequest<T>(path: string, options: RequestInit = {}): Promise<T> {
  const token = getToken()
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...options.headers,
  }
  const res = await fetch(path, { ...options, headers })
  if (res.status === 401) {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('agtech_token')
      localStorage.removeItem('agtech_email')
      window.location.href = '/login'
    }
    throw new Error('No autenticado')
  }
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(err.detail ?? 'Error en la API')
  }
  return res.json().catch(() => ({} as T)) as Promise<T>
}

export const api = {
  login: (email: string, password: string) =>
    request<{ access_token: string }>('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    }),

  me: () => request<{ email_usuario: string; nombre: string }>('/auth/me'),

  register: (email: string, nombre: string, password: string, telefono?: string) =>
    request<{ email_usuario: string; nombre: string }>('/auth/register', {
      method: 'POST',
      body: JSON.stringify({ email, nombre, password, telefono }),
    }),

  campos: () => request<Campo[]>('/campos/'),

  campo: (nombre: string) => request<Campo>(`/campos/${nombre}`),

  parcelas: (campo?: string) =>
    request<Parcela[]>(`/parcelas/${campo ? `?nombre_campo=${campo}` : ''}`),

  mapaCampo: (nombre: string) => request<MapaCampo>(`/mapa/campos/${nombre}`),

  pronostico: (nombre: string, lat: number, lon: number) =>
    request<Pronostico>(`/mapa/campos/${nombre}/pronostico?lat=${lat}&lon=${lon}`),

  alertas: (limit = 50) => request<Alerta[]>(`/alertas/?limit=${limit}`),

  predicciones: (limit = 20) => request<Prediccion[]>(`/predicciones/?limit=${limit}`),

  lecturasensor: (codigo: string, horas = 24) =>
    request<LecturaSensor[]>(`/sensores/${codigo}/lecturas?horas=${horas}`),

  ultimaLectura: (codigo: string) => request<LecturaSensor>(`/sensores/${codigo}/ultima-lectura`),

  reglas: (campo?: string) =>
    request<Regla[]>(`/reglas/${campo ? `?nombre_campo=${campo}` : ''}`),

  sensores: () => request<Sensor[]>('/sensores/'),

  asignaciones: () => request<SensorAsignacion[]>('/sensores/asignaciones'),

  crearSensor: (data: { nombre_codigo_sensor: string; estado?: string }) =>
    request<Sensor>('/sensores/', { method: 'POST', body: JSON.stringify(data) }),

  asignarSensor: (codigo: string, data: { nombre_parcela: string; nombre_campo: string; fecha_instalacion: string }) =>
    request<{ message: string; sensor: string; parcela: string }>(
      `/sensores/${codigo}/asignar`,
      { method: 'POST', body: JSON.stringify(data) }
    ),

  eliminarSensor: (codigo: string) =>
    proxyRequest<{ ok: boolean }>(`/api/proxy/sensores/${encodeURIComponent(codigo)}/eliminar`, { method: 'POST' }),

  desasignarSensor: (codigo: string, parcela: string) =>
    proxyRequest<{ ok: boolean }>(`/api/proxy/sensores/${encodeURIComponent(codigo)}/parcela/${encodeURIComponent(parcela)}/retirar`, { method: 'POST' }),

  eliminarCampo: (nombre: string) =>
    proxyRequest<{ ok: boolean }>(`/api/proxy/campos/${encodeURIComponent(nombre)}/eliminar`, { method: 'POST' }),

  eliminarParcela: (nombre: string) =>
    proxyRequest<{ ok: boolean }>(`/api/proxy/parcelas/${encodeURIComponent(nombre)}/eliminar`, { method: 'POST' }),

  eliminarRegla: (nombre: string) =>
    proxyRequest<{ ok: boolean }>(`/api/proxy/reglas/${encodeURIComponent(nombre)}/eliminar`, { method: 'POST' }),

  crearCampo: (data: Partial<Campo>) =>
    request<Campo>('/campos/', { method: 'POST', body: JSON.stringify(data) }),

  crearParcela: (data: Partial<Parcela>) =>
    request<Parcela>('/parcelas/', { method: 'POST', body: JSON.stringify(data) }),

  crearRegla: (data: Partial<Regla>) =>
    request<Regla>('/reglas/', { method: 'POST', body: JSON.stringify(data) }),

  ejecutarBatch: () =>
    request('/predicciones/ejecutar', { method: 'POST' }),

  actualizarIndices: (parcela: string, lat: number, lon: number) =>
    request(`/mapa/parcelas/${parcela}/indices-satelitales?lat=${lat}&lon=${lon}`, { method: 'POST' }),
}

// ── Tipos ──────────────────────────────────────────────────────────────────

export interface Sensor {
  nombre_codigo_sensor: string
  estado: string
}

export interface SensorAsignacion {
  nombre_codigo_sensor: string
  nombre_parcela: string
  nombre_campo: string
  fecha_instalacion: string
}

export interface Campo {
  nombre_campo: string
  coordenadas_campo?: string
  descripcion_campo?: string
}

export interface Parcela {
  nombre_parcela: string
  coordenadas_parcela?: string
  descripcion_parcela?: string
  nombre_campo: string
}

export interface Alerta {
  id_alerta: number
  fecha_emision: string
  mensaje: string
  nombre_parcela: string
  email_usuario: string
}

export interface Prediccion {
  id_prediccion: number
  fecha_emision: string
  resultado: string
  fecha_ini: string
  fecha_fin: string
  nombre_parcela: string
}

export interface LecturaSensor {
  sensor: string
  timestamp: string
  temperatura?: number
  humedad?: number
  ph?: number
}

export interface Regla {
  nombre_regla: string
  formula: string
  descripcion_regla?: string
  umbral: number
  nombre_campo: string
}

export interface MapaCampo {
  campo: string
  descripcion?: string
  coordenadas?: string
  reglas: Regla[]
  parcelas: ParcelaMapa[]
}

export interface ParcelaMapa {
  parcela: string
  descripcion?: string
  coordenadas?: object
  centro?: { lat: number; lon: number } | null
  sensores: Record<string, LecturaSensor>
  sensores_origen?: 'real' | 'simulado' | 'mixto'
  sensores_resumen?: {
    temperatura_promedio?: number | null
    humedad_promedio?: number | null
    ph_promedio?: number | null
  }
  satelital: { ndvi?: number; ndmi?: number }
  clima?: Pronostico | null
}

export interface Pronostico {
  fuente: string
  lat: number
  lon: number
  pronostico: { fecha: string; temperatura_max?: number; temperatura_min?: number; precipitacion_mm?: number }[]
}
