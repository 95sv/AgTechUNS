# AgTechUNS — Frontend

Panel de control web, separado del backend, construido con **Next.js 14
(App Router) + React + Tailwind CSS + GSAP**. Consume la API del backend
FastAPI (`../backend`) — no contiene lógica de negocio, solo presentación.

## Por qué este stack (resumen — ver explicación completa en el chat/PR)

- **Next.js / App Router**: la mayoría de las páginas son *client components*
  (`'use client'`) porque los datos (lecturas de sensores, clima, alertas)
  cambian cada pocos segundos y dependen de una sesión guardada en el
  navegador. El "renderizado híbrido" de Next no se explota a fondo en este
  proyecto académico, pero igual da buen DX: routing por archivos, soporte
  de imágenes/fuentes, y un Dockerfile estándar con `output: 'standalone'`.
- **Sin TypeScript**: el equipo definió JavaScript/React explícitamente.
- **Sin librería de estado global** (Redux/Zustand): el estado vive en
  `useState`/hooks de página; no hay necesidad de compartir estado entre
  árboles de componentes distantes.
- **Sin SWR/React Query**: un hook propio (`hooks/useParcelas.js`) con
  `fetch` + `setInterval` alcanza para una sola fuente de datos con
  polling simple, sin sumar una dependencia más.
- **react-leaflet** para el mapa: igual motor que el panel original
  (Leaflet + OpenStreetMap), pero declarativo en vez de imperativo.
- **GSAP** (`gsap` + `@gsap/react`) para las animaciones: entrada del
  header, stagger de tarjetas de parcelas y alertas, conteo animado de
  las métricas. Se centraliza el registro del plugin en `lib/gsapSetup.js`.

## Cómo se conecta con el backend

`NEXT_PUBLIC_API_URL` apunta a la URL del backend **tal como la alcanza el
navegador** (ej. `http://localhost:8000`), no el nombre del contenedor en
la red interna de Docker — porque el fetch ocurre en el cliente, no en el
servidor de Next. Por eso, en Docker, este valor se pasa como build-arg
(ver `Dockerfile` y `docker-compose.yml`): las variables `NEXT_PUBLIC_*` se
incrustan en el bundle en build time, no se leen en runtime.

El backend ya tiene CORS habilitado para `http://localhost:3000` en
`backend/main.py`.

## Desarrollo local (sin Docker)

```bash
cd frontend
npm install
cp .env.local.example .env.local   # ajustar NEXT_PUBLIC_API_URL si hace falta
npm run dev
```

Abrir [http://localhost:3000](http://localhost:3000). Requiere que el
backend (y el resto del stack de `docker-compose.yml`) esté corriendo en
`http://localhost:8000`.

## Usuarios de prueba

Los mismos del backend (`MockUserRepository`):

| Email | Password | Rol |
|---|---|---|
| admin@agtech.com | admin123 | administrador |
| agronomo@agtech.com | agronomo123 | agrónomo |
| agricultor@agtech.com | agricultor123 | agricultor |

> Nota: el login emite un JWT real, pero los endpoints `/dashboard/parcelas`
> y `/analytics/evaluar` todavía no lo exigen en el backend. La protección
> de rutas en el frontend (`components/AuthGuard.js`) es por ahora una
> guardia de UX, documentada como tal en `lib/auth.js`.

## Estructura

```
frontend/
├── app/                  Rutas (App Router): /, /login, /dashboard, /diagnostico
├── components/           UI: Header, LoginForm, MapaParcelas, ParcelaCard, ...
├── hooks/useParcelas.js  Polling de GET /dashboard/parcelas
├── lib/api.js            Cliente HTTP hacia el backend
├── lib/auth.js           Token JWT en localStorage + decodificación
└── lib/gsapSetup.js      Registro único de @gsap/react
```
