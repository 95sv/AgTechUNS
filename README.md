# AgTechUNS — Plataforma de Agricultura Inteligente

*Arquitectura y Diseño de Sistemas — Universidad Nacional del Sur — Comisión 13 — 2026*

---

## 1. Visión general

AgTechUNS es una plataforma distribuida que brinda a agricultores y agrónomos una herramienta digital para tomar decisiones informadas sobre riego, fertilización y detección temprana de enfermedades, integrando sensores IoT simulados, modelos de predicción agrícola y paneles de control en tiempo real.

Este repositorio reúne **todos** los servicios del sistema: el backend principal, el microservicio gateway hacia APIs externas, los sensores IoT simulados, el frontend web (Next.js) y la configuración de infraestructura para levantar el entorno completo con un solo comando.

## 2. Arquitectura del sistema

El sistema se compone de **ocho servicios** que se ejecutan en contenedores Docker dentro de una red interna privada. La comunicación entre servicios se resuelve por nombre (no por `localhost`), reproduciendo el esquema lógico de una arquitectura distribuida. La única excepción es el `frontend`: corre en su propio contenedor pero habla con el backend desde el **navegador** (`localhost:8000`), no por la red interna — ver sección 2.4.

```
                         Red interna Docker (agtech)
   ┌──────────────────────────────────────────────────────────────────┐
   │                                                                  │
   │   ┌────────────────────┐         ┌──────────────────────┐        │
   │   │  agtech-backend    │ ──────► │ agtech-external-     │        │
   │   │  FastAPI :8000     │  HTTP   │ gateway   FastAPI    │        │
   │   │                    │         │ :8000 (ext:8001)     │        │
   │   └──┬─────────────┬───┘         └──────────┬───────────┘        │
   │      │             │                        │                    │
   │      │             ▼                        ▼ HTTPS (egress)     │
   │      │   ┌──────────────┐         ┌─────────────────────────┐    │
   │      │   │ agtech-      │         │ Open-Meteo / Google     │    │
   │      │   │ influxdb     │         │ Earth Engine            │    │
   │      ▼   │ :8086        │         └─────────────────────────┘    │
   │   ┌──────┴───────┐ ▲                                             │
   │   │ agtech-      │ │                                             │
   │   │ postgres :5432│ │                                            │
   │   └──────────────┘ │                                             │
   │                    │                                             │
   │   ┌────────────────┴───────┐    ┌──────────────────────────┐     │
   │   │ agtech-ingestion       │◄───┤ agtech-mqtt :1883        │     │
   │   │ (worker MQTT)          │MQTT│ (broker Mosquitto)       │     │
   │   └────────────────────────┘    └──────────────▲───────────┘     │
   │                                                │ MQTT            │
   │                                ┌───────────────┴──────────┐      │
   │                                │ agtech-sensor-simulator  │      │
   │                                │ (sensores IoT simulados) │      │
   │                                └──────────────────────────┘      │
   └──────────────────────────────────────────────────────────────────┘

        ▲ HTTP (localhost:8000, fuera de la red interna)
        │
   ┌────┴────────────────┐
   │ agtech-frontend      │   ← corre en su propio contenedor (puerto host
   │ Next.js :3000        │     3000), pero el navegador del usuario es quien
   └──────────────────────┘     habla con el backend, no el contenedor en sí.
```

### 2.1 Patrón arquitectónico interno: **Arquitectura Hexagonal**

Cada servicio interno (en particular el backend) está organizado siguiendo el patrón **Hexagonal Architecture** (Ports and Adapters), propuesto por Alistair Cockburn en 2005 y también conocido como *Clean Architecture*.

La idea central es que el **dominio** (las entidades y reglas de negocio) está en el centro y no conoce a nadie. Los detalles técnicos (FastAPI, InfluxDB, MQTT, APIs externas) viven en la periferia como **adapters** que implementan **ports** definidos por el dominio. Las dependencias siempre apuntan hacia adentro.

```
       ┌─────────────────────────────────────────────────┐
       │  INFRAESTRUCTURA  (adapters secundarios)        │
       │                                                 │
       │   InfluxDB     PostgreSQL     MQTT     Gateway  │
       │       ▲             ▲          ▲          ▲    │
       │       │             │          │          │    │
       │  ┌────┴─────────────┴──────────┴──────────┴┐   │
       │  │       APLICACIÓN (casos de uso)         │   │
       │  │                                         │   │
       │  │   ┌──────────────────────────────────┐  │   │
       │  │   │       DOMINIO                    │  │   │
       │  │   │   Entidades + Ports + Reglas     │  │   │
       │  │   └──────────────────────────────────┘  │   │
       │  │                                         │   │
       │  └─────────▲───────────────────────────────┘   │
       │            │                                   │
       │   ┌────────┴──────────────┐                    │
       │   │  INTERFACES           │ (adapters          │
       │   │  HTTP / Workers       │  primarios)        │
       │   └───────────────────────┘                    │
       └─────────────────────────────────────────────────┘
```

### 2.2 Las cuatro capas del backend

| Capa | Carpeta | Qué vive ahí | De qué depende |
|---|---|---|---|
| **Dominio** | `backend/src/domain/` | Entidades del negocio (`LecturaSensor`, `Alerta`, `Usuario`), Ports (interfaces de contratos) y Reglas agronómicas puras | De nada (solo Pydantic) |
| **Aplicación** | `backend/src/application/` | Casos de uso (`IngestReading`, `EvaluateAnalytics`, `AuthenticateUser`) que orquestan operaciones del dominio | Del dominio |
| **Infraestructura** | `backend/src/infrastructure/` | Adapters que conectan con el mundo exterior: repositorios sobre InfluxDB y PostgreSQL, consumidor MQTT, cliente HTTP del gateway | Del dominio (implementa sus ports) |
| **Interfaces** | `backend/src/interfaces/` | Adapters primarios: routers HTTP de FastAPI, worker de ingesta. Son los "puntos de entrada" al sistema | De la aplicación |

### 2.3 Patrones materializados

- **Repository Pattern**: cada acceso a base de datos pasa por un repositorio que implementa un Port del dominio (ej. `InfluxDBRepository` implementa `TimeSeriesPort`).
- **Anti-Corruption Layer / Gateway Pattern**: el `External Data Gateway` es un microservicio que aísla al sistema interno del vocabulario y formatos de Open-Meteo y Google Earth Engine.
- **Patrón ETL**: el `MqttConsumer` y el caso de uso `IngestReading` materializan las tres fases (extracción del broker, transformación y validación con Pydantic, carga vía repositorio).
- **Pub/Sub asíncrono**: el broker MQTT desacopla a los sensores de la lógica de ingesta.
- **Dependency Injection**: las dependencias de FastAPI inyectan los adapters concretos en los casos de uso, permitiendo testeabilidad y evolución.

### 2.4 Separación frontend/backend

La visualización vive en `frontend/`, un servicio Next.js (React) aparte que consume `GET /dashboard/parcelas`, `GET /campos/{campo}/parcelas/{parcela}/recomendaciones`, `POST /auth/login` y `GET /diagnostico/*` por HTTP, igual que lo haría cualquier otro cliente externo.

- El backend se puede escalar, versionar y desplegar independientemente del frontend.
- El frontend puede evolucionar su stack (bundler, framework) sin tocar el backend.
- `CORSMiddleware` en `backend/main.py` ya habilita `http://localhost:3000`, el puerto donde corre el frontend.

Detalle de por qué `NEXT_PUBLIC_API_URL` apunta a `localhost:8000` y no a `http://backend:8000` (el nombre del contenedor): los fetch del frontend ocurren en el navegador del usuario, no en el servidor de Next, así que la URL tiene que ser una que la máquina host pueda resolver. Ver `frontend/README.md` para el detalle completo de decisiones de stack.

## 3. Cómo fluye una request

Recorrer mentalmente un flujo concreto es la mejor forma de entender la arquitectura. Hay tres flujos representativos:

### 3.1 Una lectura del sensor llega al sistema

```
SensorSimulator                  → publica MQTT a "agtech/sensores/SN-001"
    ↓
agtech-mqtt (broker)             → enruta al subscriptor
    ↓
MqttConsumer (infrastructure)    → recibe el mensaje, parsea JSON
    ↓
IngestReading (application)      → valida con LecturaSensor (dominio), descarta si está fuera de rango
    ↓
InfluxDBRepository (infra)       → escribe el Point en InfluxDB
```

Nótese que `IngestReading` no sabe que existe MQTT ni InfluxDB: solo conoce `LecturaSensor` y `TimeSeriesPort`.

### 3.2 Un usuario consulta el Analytics Engine

```
HTTP GET /campos/{nombre_campo}/parcelas/{nombre_parcela}/recomendaciones
    ↓
campos_router (interfaces/http)            → valida que la parcela pertenece al campo
    ↓
EvaluateAnalytics (application)            → construye el contexto consultando dos ports
    ↓    ↓
InfluxDBRepository      ExternalGatewayClient
(humedad, temperatura)  (clima ambiente)
    ↓    ↓
reglas_agronomicas (domain)                → aplica REGLAS, devuelve lista de Alerta
    ↓
campos_router                               → serializa AlertaRecomendacion[] con envelope {data, pagination}
```

> El endpoint interno `POST /analytics/evaluar` sigue disponible para uso del panel legacy (`/panel`). El contrato público del YAML Entrega 4 usa el endpoint jerárquico `/campos/.../recomendaciones`.

### 3.3 Un usuario hace login

```
HTTP POST /auth/login {email, password}
    ↓
auth_router (interfaces)               → aplica rate limiting (slowapi)
    ↓
AuthenticateUser (application)
    ↓
MockUserRepository (infrastructure)    → verifica credenciales
    ↓
AuthenticateUser                       → genera JWT con python-jose
    ↓
auth_router                            → devuelve Token al cliente
```

Cuando el repositorio relacional sobre PostgreSQL esté implementado, simplemente se reemplaza `MockUserRepository` por `PostgresUserRepository` (ambos implementan `UserRepositoryPort`). Nada más cambia.

## 4. Estructura del repositorio

```
AgTechUNS/
├── README.md                     Este documento
├── docker-compose.yml            Orquestador de los siete servicios
├── .gitignore
├── .dockerignore
│
├── backend/                      SERVICIO: Backend principal (solo API)
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── main.py                   Composition root (ensamblado de FastAPI)
│   └── src/
│       ├── domain/
│       │   ├── entities/         LecturaSensor, Alerta, Usuario
│       │   ├── ports/            TimeSeriesPort, WeatherPort, UserRepositoryPort
│       │   └── rules/            Reglas agronómicas del Analytics Engine
│       ├── application/          IngestReading, EvaluateAnalytics, AuthenticateUser
│       ├── infrastructure/
│       │   ├── persistence/      InfluxDBRepository, MockUserRepository
│       │   ├── messaging/        MqttConsumer
│       │   ├── external/         ExternalGatewayClient
│       │   └── config.py
│       └── interfaces/
│           ├── http/             Routers FastAPI + inyección de dependencias
│           └── workers/          ingestion_worker (proceso MQTT background)
│
├── frontend/                     SERVICIO: Frontend web (Next.js + React)
│   ├── Dockerfile
│   ├── package.json
│   ├── app/                      Rutas: /, /login, /dashboard, /diagnostico
│   ├── components/               Header, LoginForm, MapaParcelas, ParcelaCard...
│   ├── hooks/                    useParcelas (polling de GET /dashboard/parcelas)
│   └── lib/                      Cliente HTTP, manejo de sesión JWT
│
├── external-gateway/             SERVICIO: Anti-Corruption Layer
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app/                      Adapter HTTP hacia Open-Meteo y GEE
│
├── simulator/                    SERVICIO: Sensores IoT simulados
│   ├── Dockerfile
│   ├── requirements.txt
│   └── sensor_simulator.py
│
├── config/
│   └── parcelas.json             Parcelas y sensores usados por backend y simulador
│
└── infra/
    └── mosquitto/config/         Configuración del broker MQTT
```

## 5. Cómo agregar funcionalidad nueva

La arquitectura responde a las preguntas más frecuentes del equipo. Si alguien pregunta *"¿dónde pongo X?"*, la respuesta sale del layout:

| Quiero agregar... | Dónde va |
|---|---|
| Una entidad nueva (ej. `Campo`, `Parcela`) | `backend/src/domain/entities/` |
| Una regla agronómica nueva | `backend/src/domain/rules/reglas_agronomicas.py` (sumar a la lista `REGLAS`) |
| Un caso de uso nuevo (ej. "registrar nuevo campo") | `backend/src/application/` |
| Integración con un nuevo sistema externo | `backend/src/infrastructure/external/` + un Port en `domain/ports/` |
| Una nueva base de datos | `backend/src/infrastructure/persistence/` |
| Un endpoint HTTP nuevo | `backend/src/interfaces/http/` y registrar en `main.py` |
| Un proceso background nuevo | `backend/src/interfaces/workers/` y agregar al `docker-compose.yml` |
| Un endpoint nuevo en el Gateway | `external-gateway/app/main.py` |
| Una parcela/sensor simulado nuevo | `config/parcelas.json` y reiniciar backend + simulador |

## 6. Pre-requisitos

- **Docker Desktop** instalado y en ejecución (con virtualización del sistema habilitada en la BIOS).
- **Git** instalado y configurado.
- Sin necesidad de instalar Python, Node.js ni nada más: los contenedores resuelven el entorno completo.

## 7. Cómo levantar el sistema

Clonar el repositorio y ejecutar desde su raíz:

```bash
git clone https://github.com/<usuario>/AgTechUNS.git
cd AgTechUNS
docker compose up -d
```

La primera ejecución descarga las imágenes base y construye los servicios de aplicación (backend/ingestion, gateway y simulator), lo cual puede tomar varios minutos. Las siguientes arrancan en segundos.

### 7.1 Verificación de despliegue

```bash
docker compose ps
```

Deben listarse los ocho contenedores en estado `running`/`Up`. Esperando aproximadamente treinta segundos posteriores al arranque, en el navegador:

```
http://localhost:8000/diagnostico/integracion
```

La respuesta debe ser un JSON donde `stack_ok: true` indica que las dos fuentes de datos (InfluxDB y External Gateway) están conectadas y funcionando.

Para visualizar la aplicación web, abrir:

```
http://localhost:3000
```

Redirige a `/login` (usuarios de prueba: `admin@agtech.com` / `admin123`, ver `frontend/README.md`) y de ahí a `/dashboard`, que consulta periódicamente `GET /dashboard/parcelas` para mostrar el estado de las parcelas, las últimas lecturas de sensores y el clima ambiente. El botón **Evaluar análisis** dispara `POST /analytics/evaluar`. La build de Next ya empaqueta sus estilos (Tailwind) y dependencias (Leaflet, GSAP); solo se necesita internet para los tiles de OpenStreetMap del mapa.

### 7.2 Endpoints expuestos

| URL | Función |
|---|---|
| `http://localhost:3000` | Frontend web (login + panel de monitoreo) |
| `http://localhost:8000/panel` | Panel de control HTML legacy (admin) |
| `http://localhost:8000/docs` | Swagger del backend — contrato YAML Entrega 4 |
| `http://localhost:8001/docs` | Swagger del External Gateway |
| `http://localhost:8086` | UI de InfluxDB (`admin` / `agtech-admin-pass`) |
| `http://localhost:8000/diagnostico/integracion` | Verificación end-to-end |
| `http://localhost:8000/dashboard/parcelas` | Datos agregados para el frontend Next.js (GET) |
| `http://localhost:8000/auth/login` | Login JWT — acepta `{ emailUsuario, password }` (POST) |
| `http://localhost:8000/auth/logout` | Cierre de sesión (POST) |
| `http://localhost:8000/campos` | CRUD de campos con paginación `{data, pagination}` (GET/POST) |
| `http://localhost:8000/campos/{campo}/parcelas` | Parcelas de un campo (GET/POST/DELETE) |
| `http://localhost:8000/campos/{campo}/parcelas/{parcela}/recomendaciones` | Alertas analíticas (GET) |
| `http://localhost:8000/campos/{campo}/parcelas/{parcela}/predicciones` | Predicciones batch — stub CU-06 (GET) |
| `http://localhost:8000/cultivos` | Catálogo de cultivos con paginación (GET/POST/DELETE) |
| `http://localhost:8000/reglas` | Catálogo de reglas agronómicas (GET/POST) |
| `http://localhost:8000/usuarios` | Gestión de usuarios (POST — requiere admin) |
| `http://localhost:8000/external/weather` | Clima vía External Gateway (GET) |
| `http://localhost:8000/external/satelital` | Índices satelitales — stub (GET) |
| `http://localhost:8001/weather?lat=-38.71&lon=-62.27` | Clima directo desde External Gateway |
| `http://localhost:8001/satellite/1?lat=-38.71&lon=-62.27` | Índices satelitales desde External Gateway |

### 7.3 Comandos frecuentes

```bash
docker compose logs -f backend          # ver logs en vivo
docker compose logs -f ingestion        # ver lecturas siendo guardadas

docker compose up -d --build backend    # rebuild de un servicio tras cambios
docker compose up -d --build            # rebuild de todo

docker compose down                     # detener (conservando datos)
docker compose down -v                  # detener y borrar datos
```

## Panel de Control: cómo usarlo

El sistema incluye un **panel web** servido por el backend en `http://localhost:8000/panel`. La interfaz se construyó como SPA estática con tres librerías cargadas por CDN (Tailwind CSS para estilos, Leaflet para el mapa, Alpine.js para la reactividad) y no requiere instalar Node.js ni ejecutar ningún build.

### Autenticación

El acceso al panel es público para visualización. Las funciones de gestión (CRUD de campos, parcelas y cultivos) requieren autenticación con rol **administrador**. La autenticación es vía JWT emitido por `POST /auth/login` y se almacena en `localStorage`.

Usuarios de prueba (mock — pendiente repositorio relacional sobre PostgreSQL):

| Email | Contraseña | Rol |
|---|---|---|
| `admin@agtech.com` | `admin123` | administrador |
| `agronomo@agtech.com` | `agronomo123` | agrónomo |
| `agricultor@agtech.com` | `agricultor123` | agricultor |

Solo el rol `administrador` ve las pestañas de gestión. La autorización se valida tanto en el frontend (oculta pestañas) como en el backend (las rutas de escritura usan la dependencia `require_admin`).

### Vistas del panel

| Vista | Función | Acceso |
|---|---|---|
| 📊 Dashboard | Mapa con marcadores de parcelas, cards con humedad/temperatura del sensor + clima ambiente, botón para disparar el Analytics Engine y visualizar alertas | Todos |
| 🌍 Campos | Listar / crear / eliminar campos (entidad `Campo`) | Solo admin |
| 📍 Parcelas | Listar / crear / eliminar parcelas. El campo asociado se elige de un dropdown con los campos existentes | Solo admin |
| 🌱 Cultivos | Catálogo de variedades sembrables (entidad `Cultivo`) | Solo admin |

### Flujo típico del administrador

1. Iniciar sesión como admin.
2. Crear los **campos** que va a manejar.
3. Cargar el **catálogo de cultivos** (variedades).
4. Crear las **parcelas**, eligiendo el campo correspondiente del dropdown.
5. Reiniciar el simulador para que publique las lecturas de los sensores nuevos:
```bash
   docker compose restart sensor-simulator
```
6. Los datos empiezan a verse en el dashboard a los pocos segundos.

### Decisión arquitectónica: panel servido por el backend

El panel se sirve como archivos estáticos desde el backend mediante `StaticFiles` de FastAPI. Esta decisión simplifica el despliegue para el alcance académico (un único contenedor para API + UI, sin necesidad de Node.js ni build pipeline). En un escenario productivo, lo idiomático sería migrar el panel a un servicio frontend independiente (Next.js u otra SPA con su propia infraestructura de despliegue) — esta migración queda documentada como trabajo futuro.

## 8. Estado de implementación

### 8.1 Operativo
- Autenticación JWT con rate limiting (3 usuarios mock: admin, agrónomo, agricultor). Login con campo `emailUsuario` conforme al YAML.
- Ingesta IoT completa: simulador → MQTT → worker → validación → InfluxDB. Los tres sensores (SN-001, SN-002, SN-003) publican y se visualizan.
- External Data Gateway con endpoint de clima funcional.
- Analytics Engine MVP con tres reglas agronómicas que cruzan sensor y clima.
- Frontend Next.js separado del backend (`frontend/`), con login, mapa, filtros de parcelas, trigger manual de analytics y página de diagnóstico — ver `frontend/README.md`.
- Panel HTML legacy en `/panel`, servido por FastAPI `StaticFiles`.
- Endpoint de diagnóstico end-to-end.

### 8.2 Contrato API — Alineación con YAML Entrega 4

La implementación respeta el contrato definido en `Entrega 4/Diseño APIs/api-agtechuns.yaml`:

| Aspecto | YAML Entrega 4 | Implementación |
|---|---|---|
| Jerarquía de recursos | `/campos/{campo}/parcelas/{parcela}/recomendaciones` | ✅ Implementado |
| Envelope de respuesta | `{ data: [...], pagination: { page, limit, total, total_pages } }` | ✅ En todos los GET de colecciones |
| Campo de login | `emailUsuario` | ✅ Alias Pydantic `email_usuario` |
| Entidad Campo | `coordenadas_campo` | ✅ Renombrado desde `ubicacion` |
| Entidad Cultivo | `nombre_cultivo`, `umbral_humedad_minima` | ✅ Renombrado y extendido |
| Alertas analíticas | `AlertaRecomendacion` plano con `subtipo`, `severidad`, `fecha_emision`, `mensaje` | ✅ Implementado |
| `/auth/refresh`, `/auth/logout` | Stubs conforme al contrato | ✅ Rutas activas (MVP stateless) |
| `/reglas`, `/usuarios` | Gestión de reglas y usuarios | ✅ Stubs activos con validación de rol |
| `/external/weather`, `/external/satelital` | Datos externos | ✅ Weather funcional, satelital stub |
| Predicciones CU-06 | Predicciones batch | Stub — módulo en desarrollo |

Ver `docs/trazabilidad_componentes.md` para el mapa completo de componentes documentados vs. implementados.

### 8.3 Postergado con justificación documentada
- Batch Scheduler nocturno (CU-06): stub `GET .../predicciones` disponible, lógica pendiente.
- Repositorio relacional sobre PostgreSQL: contenedor levantado, adapter JSON usado como sustituto temporal.
- Servicio de Notificaciones por correo: estudio de viabilidad documentado.
- Motor de reglas dinámico configurable: `GET/POST /reglas` disponible, persistencia en memoria.
- Análisis satelital con credenciales reales de GEE: dependencia externa fuera del alcance temporal.

## 9. Equipo

Comisión 13 — *Arquitectura y Diseño de Sistemas — UNS 2026*
Docente responsable: Paola Budan.
