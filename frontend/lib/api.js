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
  // Auth — usa emailUsuario conforme contrato YAML Entrega 4
  login: ({ email, password }) =>
    request('/auth/login', { method: 'POST', body: { emailUsuario: email, password } }),

  // Dashboard — endpoint interno de agregación (no en YAML público)
  getParcelas: () => request('/dashboard/parcelas'),

  // Analytics — evaluación por parcela (GET /campos/{campo}/parcelas/{parcela}/recomendaciones)
  getRecomendaciones: (nombreCampo, nombreParcela) =>
    request(
      `/campos/${encodeURIComponent(nombreCampo)}/parcelas/${encodeURIComponent(nombreParcela)}/recomendaciones`,
      { auth: true }
    ),

  // Diagnóstico
  getHealth: () => request('/diagnostico/health'),
  getIntegracion: (params = {}) => {
    const qs = new URLSearchParams(params).toString();
    return request(`/diagnostico/integracion${qs ? `?${qs}` : ''}`);
  },
};
