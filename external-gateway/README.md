# External Data Gateway

Microservicio en FastAPI que implementa el **patrón Anti-Corruption Layer**
frente a dos APIs externas: Google Earth Engine (índices NDVI/NDMI) y
Open-Meteo (datos climáticos).

El backend principal nunca conoce los detalles de esas APIs: solo habla con
este microservicio a través de su cliente HTTP (`backend/src/infrastructure/external/gateway_client.py`).

## Endpoints

- `GET /weather?lat=&lon=` — temperatura ambiente actual
- `GET /satellite/{parcel_id}?lat=&lon=` — índices NDVI/NDMI (requiere credenciales GEE)
- `GET /docs` — documentación interactiva Swagger
