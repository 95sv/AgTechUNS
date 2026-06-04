# AgTechUNS — Plataforma de Monitoreo Agrícola
Universidad Nacional del Sur · Arquitectura y Diseño de Sistemas · Comisión 13

---

## Arquitectura del Sistema

```
Sensores IoT → MQTT Broker → IoT Ingestion (ETL) → InfluxDB
                                                          ↓
Open-Meteo API ─────────────────────────────→ Analytics Engine (batch diario)
Google Earth Engine (simulado)  ──────────→         ↓
                                              PostgreSQL (alertas, predicciones)
                                                          ↓
Frontend (Next.js) ←──── REST API (FastAPI) ────────────→ SendGrid
```

## Levantar el sistema (Docker)

```bash
# 1. Copiar variables de entorno
cp .env.example .env

# 2. Levantar toda la infraestructura
docker compose up -d

# 3. Verificar servicios
#   Frontend:   http://localhost:3000
#   Backend:    http://localhost:8000/docs  (Swagger UI)
#   InfluxDB:   http://localhost:8086
#   MQTT:       localhost:1883
```

## Uso completo del sistema

Para que el sistema completo funcione y se puedan ver las lecturas simuladas, el orden recomendado es:

### Quick Start en 3 pasos

1. Copiar el archivo de ejemplo de variables de entorno que viene versionado en el repo: `cp .env.example .env`
2. Levantar la infraestructura con Docker: `docker compose up -d`
3. Ejecutar el simulador IoT en otra terminal y luego abrir `http://localhost:3000` para entrar al `Mapa`

Después de esos pasos, verificá que queden disponibles backend, frontend, PostgreSQL, InfluxDB y Mosquitto. Luego abrí una segunda terminal y ejecutá el simulador IoT:

```bash
cd iot-simulator
pip install -r requirements.txt
python lns_console.py
```

En el menú del simulador:
    - Crear un campo
    - Registrar al menos una gateway
    - Registrar uno o más sensores
    - Iniciar la transmisión

Si querés ver las lecturas, entrá a `Mapa` y seleccioná el campo creado.

El archivo `.env.example` es la plantilla de variables compartida por el equipo. Se copia a `.env` en la raíz del proyecto para que Docker y el backend lean la configuración real sin versionar secretos ni credenciales locales. Si el backend corre fuera de Docker, además hay que levantar manualmente PostgreSQL, InfluxDB y Mosquitto, y ajustar las variables de conexión en `.env`.

## Desarrollo local (sin Docker)

### Backend
```bash
cd backend
pip install -r requirements.txt

# Necesita PostgreSQL, InfluxDB y Mosquitto corriendo localmente
# Ajustar variables en .env

uvicorn app.main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev   # → http://localhost:3000
```

### Simulador IoT
```bash
cd iot-simulator
pip install -r requirements.txt
python lns_console.py
```

El simulador publica lecturas por MQTT en `agtech/sensores/<device_id>`. Cuando la ingesta está funcionando, esos datos se reflejan en la vista `Mapa` y en el panel lateral de cada parcela.

## Flujo de datos — Pipeline IoT

1. Abrir el **LNS Console** (`python lns_console.py`)
2. Crear un campo → registrar una gateway → registrar sensores
3. Iniciar transmisión (opción 3 del menú)
4. Los sensores publican cada 10 s al tópico `agtech/sensores/<device_id>`
5. El **IoT Ingestion Service** del backend consume el MQTT, valida y escribe en InfluxDB
6. La UI del **Mapa** muestra las últimas lecturas en tiempo real

## Analytics Engine (batch)

- Se ejecuta diariamente a las 02:00 UTC (configurable en `.env`)
- Evalúa las **Reglas Agroclimáticas** configuradas por el Administrador
- Si se supera un umbral → genera **Predicción** + **Alerta** + email vía SendGrid
- Se puede disparar manualmente desde la UI: `Recomendaciones > Ejecutar análisis ahora`

## API REST

Documentación interactiva disponible en: `http://localhost:8000/docs`

| Endpoint | Descripción |
|----------|-------------|
| `POST /auth/login` | Autenticación JWT |
| `GET /campos/` | Listar campos |
| `GET /mapa/campos/{nombre}` | CU-01: mapa consolidado |
| `GET /alertas/` | Listar alertas |
| `GET /predicciones/` | CU-02: recomendaciones |
| `POST /predicciones/ejecutar` | Disparar batch manual |
| `GET /sensores/{codigo}/lecturas` | Serie temporal InfluxDB |
| `POST /reglas/` | CU-07: crear regla agroclimática |

## Reglas Agroclimáticas (CU-07)

Fórmulas disponibles:
- `humedad_promedio_menor_que` — riesgo de estrés hídrico
- `temperatura_menor_que` — riesgo de helada
- `temperatura_mayor_que` — estrés calórico
- `ph_fuera_de_rango` — anomalía de pH del suelo

## Stack Tecnológico

| Capa | Tecnología |
|------|-----------|
| Frontend | Next.js 14 (TypeScript) + Tailwind CSS + Leaflet |
| Backend | FastAPI (Python 3.12) + SQLAlchemy async |
| BD Relacional | PostgreSQL 16 |
| BD Series Temporales | InfluxDB 2.7 |
| Mensajería IoT | MQTT (Eclipse Mosquitto) |
| Notificaciones | SendGrid |
| Clima | Open-Meteo API |
| Imágenes Satelitales | Google Earth Engine (simulado) |
| Contenedores | Docker Compose |
