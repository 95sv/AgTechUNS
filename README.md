# AgTechUNS — Plataforma de Agricultura Inteligente

*Arquitectura y Diseño de Sistemas — Universidad Nacional del Sur — Comisión 13 — 2026*

---

## 1. Visión general

AgTechUNS es una plataforma distribuida que brinda a agricultores y agrónomos una herramienta digital para tomar decisiones informadas sobre riego, fertilización y detección temprana de enfermedades, integrando sensores IoT simulados, modelos de predicción agrícola y paneles de control en tiempo real.

Este repositorio reúne **todos** los servicios del sistema: el backend principal, el microservicio gateway hacia APIs externas, los sensores IoT simulados, el frontend Next.js y la configuración de infraestructura para levantar el entorno completo con un solo comando.

## 2. Arquitectura del sistema

El sistema se compone de **siete servicios** que se ejecutan en contenedores Docker dentro de una red interna privada. La comunicación entre servicios se resuelve por nombre (no por `localhost`), reproduciendo el esquema lógico de una arquitectura distribuida.

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
HTTP POST /analytics/evaluar
    ↓
analytics_router (interfaces/http)         → recibe la request HTTP
    ↓
EvaluateAnalytics (application)            → construye el contexto consultando dos ports
    ↓    ↓
InfluxDBRepository      ExternalGatewayClient
(humedad, temperatura)  (clima ambiente)
    ↓    ↓
reglas_agronomicas (domain)                → aplica REGLAS, devuelve lista de Alerta
    ↓
analytics_router                            → serializa a JSON y responde
```

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
├── backend/                      SERVICIO: Backend principal
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
├── frontend/                     Frontend Next.js (a migrar del repo original)
│   └── ...
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

La primera ejecución descarga las imágenes base y construye los tres servicios (backend, gateway, simulator), lo cual puede tomar varios minutos. Las siguientes arrancan en segundos.

### 7.1 Verificación de despliegue

```bash
docker compose ps
```

Deben listarse los siete contenedores en estado `running`/`Up`. Esperando aproximadamente treinta segundos posteriores al arranque, en el navegador:

```
http://localhost:8000/diagnostico/integracion
```

La respuesta debe ser un JSON donde `stack_ok: true` indica que las dos fuentes de datos (InfluxDB y External Gateway) están conectadas y funcionando.

### 7.2 Endpoints expuestos

| URL | Función |
|---|---|
| `http://localhost:8000/docs` | Swagger del backend principal |
| `http://localhost:8001/docs` | Swagger del External Gateway |
| `http://localhost:8086` | UI de InfluxDB (`admin` / `agtech-admin-pass`) |
| `http://localhost:8000/diagnostico/integracion` | Verificación end-to-end |
| `http://localhost:8000/auth/login` | Login JWT (POST) |
| `http://localhost:8000/analytics/evaluar` | Disparar Analytics Engine (POST) |

### 7.3 Comandos frecuentes

```bash
docker compose logs -f backend          # ver logs en vivo
docker compose logs -f ingestion        # ver lecturas siendo guardadas

docker compose up -d --build backend    # rebuild de un servicio tras cambios
docker compose up -d --build            # rebuild de todo

docker compose down                     # detener (conservando datos)
docker compose down -v                  # detener y borrar datos
```

## 8. Estado de implementación

### 8.1 Operativo
- Autenticación JWT con rate limiting (3 usuarios mock: admin, agrónomo, agricultor).
- Ingesta IoT completa: simulador → MQTT → worker → validación → InfluxDB.
- External Data Gateway con endpoint de clima funcional.
- Analytics Engine MVP con tres reglas agronómicas que cruzan sensor y clima.
- Endpoint de diagnóstico end-to-end.

### 8.2 En curso (Entrega 4)
- Decisiones Arquitectónicas (ADRs).
- Diseño de APIs (OpenAPI 3.0).
- Pipeline de Datos.
- Estudios de Viabilidad.

### 8.3 Postergado con justificación documentada
- Batch Scheduler nocturno (CU-06): sustituido por trigger manual via endpoint.
- Repositorio relacional sobre PostgreSQL: pendiente en próxima iteración.
- Servicio de Notificaciones por correo: estudio de viabilidad.
- Motor de reglas dinámico configurable: estudio de viabilidad.
- Análisis satelital con credenciales reales de GEE: dependencia externa fuera del alcance temporal.

## 9. Equipo

Comisión 13 — *Arquitectura y Diseño de Sistemas — UNS 2026*
Docente responsable: Paola Budan.
