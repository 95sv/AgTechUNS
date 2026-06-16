/**
 * Cliente HTTP centralizado hacia el backend AgTechUNS (FastAPI).
 *
 * Decisión de diseño: un único punto que conoce la URL base y el formato
 * de error del backend, en vez de repetir fetch() en cada componente.
 * Equivalente, a escala de frontend, al rol que cumple un Adapter en la
 * arquitectura hexagonal del backend: aísla al resto de la app del detalle
 * de transporte (HTTP, JSON, headers).
 */
import { getToken } from './auth';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

async function request(path, { method = 'GET', body, auth = false } = {}) {
  const headers = { 'Content-Type': 'application/json' };
  if (auth) {
    const token = getToken();
    if (token) headers.Authorization = `Bearer ${token}`;
  }

  let res;
  try {
    res = await fetch(`${API_URL}${path}`, {
      method,
      headers,
      body: body ? JSON.stringify(body) : undefined,
    });
  } catch (err) {
    throw new Error(`No se pudo conectar con el backend (${API_URL}). ¿Está corriendo?`);
  }

  const isJson = res.headers.get('content-type')?.includes('application/json');
  const data = isJson ? await res.json() : null;

  if (!res.ok) {
    const detail = data?.detail || data?.message || `Error ${res.status}`;
    throw new Error(typeof detail === 'string' ? detail : JSON.stringify(detail));
  }
  return data;
}

export const api = {
  login: (credenciales) => request('/auth/login', { method: 'POST', body: credenciales }),
  getParcelas: () => request('/dashboard/parcelas'),
  evaluarAnalytics: () => request('/analytics/evaluar', { method: 'POST' }),
  getHealth: () => request('/diagnostico/health'),
  getIntegracion: (params = {}) => {
    const qs = new URLSearchParams(params).toString();
    return request(`/diagnostico/integracion${qs ? `?${qs}` : ''}`);
  },
};
