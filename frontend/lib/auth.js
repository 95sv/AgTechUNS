/**
 * Manejo de sesión en el cliente.
 *
 * Decisión: el token JWT se guarda en localStorage y la sesión se valida
 * solo en el cliente (AuthGuard redirige a /login si no hay token).
 *
 * Esto es una simplificación deliberada para el alcance académico del
 * proyecto: ni `/dashboard/parcelas` ni `/analytics/evaluar` exigen hoy
 * el header Authorization en el backend (no hay un Depends(get_current_user)
 * en esos routers todavía). El login real contra AuthenticateUser/JWT
 * funciona de punta a punta, pero la protección de rutas es, por ahora,
 * una guardia de UX en el frontend, no un control de seguridad del backend.
 * Si se agrega esa verificación en el backend, alcanza con que `api.js`
 * ya manda el Authorization header (parámetro `auth: true`) para que todo
 * siga funcionando sin tocar componentes.
 *
 * Para producción real, lo correcto sería una cookie httpOnly + verificación
 * server-side; se documenta como decisión pendiente, no como descuido.
 */
const TOKEN_KEY = 'agtech_token';

export function saveToken(token) {
  if (typeof window === 'undefined') return;
  window.localStorage.setItem(TOKEN_KEY, token);
}

export function getToken() {
  if (typeof window === 'undefined') return null;
  return window.localStorage.getItem(TOKEN_KEY);
}

export function clearToken() {
  if (typeof window === 'undefined') return;
  window.localStorage.removeItem(TOKEN_KEY);
}

/** Decodifica el payload de un JWT sin validar la firma (solo para UI). */
export function decodeToken(token) {
  try {
    const payload = token.split('.')[1];
    const base64 = payload.replace(/-/g, '+').replace(/_/g, '/');
    const json = decodeURIComponent(
      atob(base64)
        .split('')
        .map((c) => '%' + c.charCodeAt(0).toString(16).padStart(2, '0'))
        .join('')
    );
    return JSON.parse(json);
  } catch {
    return null;
  }
}

/** Devuelve { email, roles } del usuario logueado, o null si no hay sesión válida. */
export function getUsuario() {
  const token = getToken();
  if (!token) return null;
  const payload = decodeToken(token);
  if (!payload) return null;
  if (payload.exp && Date.now() / 1000 > payload.exp) {
    clearToken();
    return null;
  }
  return { email: payload.sub, roles: payload.roles || [] };
}
