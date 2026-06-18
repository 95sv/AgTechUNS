# Trazabilidad entre documentacion e implementacion - AgTechUNS

Este documento resume como se reflejan en el codigo los componentes definidos en la documentacion y en el diagrama de componentes. La idea es que el grupo tenga una explicacion clara para defender la implementacion frente a la documentacion entregada.

## Respuesta corta

La implementacion actual no copia literalmente los nombres del diagrama en carpetas o clases, pero si materializa varios componentes mediante routers, casos de uso, repositorios, workers y servicios Docker.

El diagrama representa la arquitectura objetivo. El codigo implementa un MVP funcional que respeta las fronteras principales: frontend separado, backend FastAPI, ingesta MQTT, repositorio de series temporales, gateway externo y motor analitico simplificado. Algunos componentes quedaron implementados de forma temporal o postergados por alcance.

La forma correcta de explicarlo es:

> La documentacion define componentes logicos. En el codigo esos componentes se implementan como modulos, adapters, routers, servicios Docker o casos de uso. No siempre existe una carpeta con el mismo nombre, pero si existe una correspondencia arquitectonica.

## Mapa de componentes

| Componente documentado | Donde esta en el codigo | Estado | Explicacion |
|---|---|---|---|
| SPA | `frontend/` | Implementado | Es la aplicacion Next.js que consume el backend por HTTP. |
| API Controller | `backend/main.py`, `backend/src/interfaces/http/` | Implementado | Son los routers FastAPI. Reciben requests REST y delegan a casos de uso o repositorios. |
| Sign In Controller | `backend/src/interfaces/http/auth_router.py`, `backend/src/application/authenticate_user.py` | Implementado MVP | Expone `/auth/login`, valida credenciales mock y emite JWT. |
| Security Controller | `backend/src/interfaces/http/auth_dependency.py` | Implementado MVP | Valida JWT y roles. Protege rutas administrativas con `require_admin`. |
| Analytics Engine | `backend/src/application/evaluate_analytics.py`, `backend/src/domain/rules/reglas_agronomicas.py` | Implementado MVP | Ejecuta reglas agronomicas simples cruzando datos de sensores y clima. |
| Time Series Repository | `backend/src/infrastructure/persistence/influxdb_repository.py` | Implementado | Encapsula InfluxDB. Guarda lecturas y calcula ultima lectura/promedios. |
| IoT Ingestion Component | `backend/src/interfaces/workers/ingestion_worker.py`, `backend/src/infrastructure/messaging/mqtt_consumer.py`, `backend/src/application/ingest_reading.py` | Implementado MVP | Escucha MQTT, parsea JSON, valida lecturas y las persiste en InfluxDB. |
| Broker MQTT | `docker-compose.yml`, `infra/mosquitto/config/mosquitto.conf` | Implementado | Se usa Eclipse Mosquitto como broker para desacoplar sensores e ingesta. |
| Sensores IoT | `simulator/sensor_simulator.py` | Implementado como simulador | Publica lecturas simuladas de temperatura y humedad por MQTT. |
| External Data Gateway | `external-gateway/app/main.py`, `external-gateway/app/gateway.py`, `backend/src/infrastructure/external/gateway_client.py` | Implementado | Microservicio separado que consulta Open-Meteo y tiene soporte para datos satelitales. |
| Relational Repository | `json_campo_repository.py`, `json_parcela_repository.py`, `json_cultivo_repository.py`, `mock_user_repository.py` | Implementado temporalmente | La documentacion plantea PostgreSQL; el MVP usa JSON/mock como adapter temporal para datos operativos. PostgreSQL está en Docker Compose listo para migrar. |
| Contrato API (YAML Entrega 4) | `backend/src/interfaces/http/campos_router.py`, `cultivos_router.py`, `auth_router.py`, `reglas_router.py`, `usuarios_router.py`, `external_router.py` | Implementado | Rutas jerárquicas, envelope `{data, pagination}`, `emailUsuario`, `AlertaRecomendacion` y stubs de CU-06 alineados con el YAML entregado. |
| DB Relacional PostgreSQL | `docker-compose.yml` | Parcial | El contenedor existe, pero el backend todavia no lo usa como persistencia real. |
| Notification Component | No implementado | Postergado | No hay WebSockets, SMTP/API externa ni push de alertas. |
| Notification Service externo | No implementado | Postergado | No hay integracion con SendGrid, Twilio, SMTP u otro proveedor. |
| Reset Password Controller | No implementado | Postergado | No existe flujo de recuperacion de contrasena. |
| Batch Scheduler | No implementado | Reemplazado temporalmente | El analisis se dispara manualmente con `POST /analytics/evaluar`. |
| Catalogo dinamico de reglas | No implementado | Postergado | Las reglas estan hardcodeadas en `reglas_agronomicas.py`. |

## Como explicar por que los nombres no coinciden exactamente

No es necesariamente un error que el codigo no tenga carpetas llamadas literalmente `Analytics Engine` o `API Controller`. En arquitectura, esos nombres son componentes logicos. En una implementacion con arquitectura hexagonal o clean architecture, esos componentes suelen dividirse en:

- **Routers**: entrada HTTP del sistema.
- **Casos de uso**: logica de aplicacion.
- **Entidades y reglas de dominio**: logica pura del negocio.
- **Adapters de infraestructura**: repositorios, clientes HTTP, consumidores MQTT.
- **Servicios Docker**: componentes desplegables.

Por ejemplo, el `Analytics Engine` no aparece como una carpeta con ese nombre porque se materializa en:

- `evaluate_analytics.py`: orquestacion del analisis.
- `reglas_agronomicas.py`: reglas del dominio.
- `analytics_router.py`: endpoint que dispara el analisis.

Lo mismo ocurre con `API Controller`: no es una clase unica, sino el conjunto de routers FastAPI en `backend/src/interfaces/http/`.

## Puntos que si pueden ser observados por la profesora

Los riesgos principales no son de nombres, sino de diferencias funcionales entre documentacion e implementacion.

1. **PostgreSQL documentado vs JSON/mock implementado**

   La documentacion dice que usuarios, campos, parcelas, cultivos, reglas, alertas y predicciones viven en PostgreSQL mediante un Relational Repository. En el codigo, esa parte se resolvio con archivos JSON y usuarios mock.

   Respuesta sugerida:

   > PostgreSQL esta previsto y levantado en Docker Compose, pero para este MVP se uso un adapter temporal basado en JSON/mock. La arquitectura mantiene el patron Repository, por lo que reemplazarlo por un repositorio PostgreSQL no cambia los routers ni los casos de uso.

2. **Notification Component ausente**

   El diagrama incluye notificaciones por WebSocket y servicio externo, pero el codigo no tiene ese modulo.

   Respuesta sugerida:

   > El Notification Component forma parte de la arquitectura objetivo. En esta iteracion se priorizo la generacion de alertas dentro del Analytics Engine y su visualizacion en el dashboard. El envio push/WebSocket queda postergado.

3. **Reset Password no implementado**

   El diagrama muestra el controlador de recuperacion de contrasena, pero el backend actual solo tiene login y `/auth/me`.

   Respuesta sugerida:

   > El flujo de recuperacion de cuenta fue documentado como parte del diseno completo, pero no se implemento en el MVP. La autenticacion principal con JWT si esta implementada.

4. **Batch Scheduler reemplazado por trigger manual**

   La documentacion del pipeline habla de procesamiento nocturno. El codigo usa `POST /analytics/evaluar`.

   Respuesta sugerida:

   > El pipeline analitico batch quedo representado por un trigger manual para la entrega parcial. El caso de uso `EvaluateAnalytics` encapsula la logica que luego podria ser ejecutada por un scheduler sin cambiar el motor.

5. **OpenAPI entregado alineado con la implementación actual**

   El contrato YAML de Entrega 4 fue implementado íntegramente. Las rutas jerárquicas de parcelas bajo campos (`/campos/{campo}/parcelas/{parcela}/recomendaciones`), el envelope `{data, pagination}`, el campo `emailUsuario` en login, los nombres de entidad actualizados (`coordenadas_campo`, `nombre_cultivo`) y el esquema `AlertaRecomendacion` están todos implementados y funcionando.

   Los stubs activos (predicciones CU-06, `/reglas` con memoria, `/usuarios` con validación de rol) representan los endpoints definidos en el YAML pero con implementación parcial por alcance.

## Que conviene hacer antes de entregar o presentar

### Opcion rapida

Agregar este documento al repositorio y mencionarlo en el README como "Trazabilidad entre arquitectura e implementacion".

Ventaja: deja claro que las diferencias son conocidas y justificadas.

### Opcion intermedia

Actualizar el README con una seccion breve:

```md
## Trazabilidad arquitectura-implementacion

La arquitectura documentada define componentes logicos. En este repositorio se implementan como routers FastAPI, casos de uso, adapters, workers y servicios Docker. Ver `docs/trazabilidad_componentes.md`.
```

### Opcion mas completa

Ademas de documentar, ajustar nombres visibles:

- Tags de Swagger.
- README.
- Nombres de servicios Docker.
- Comentarios/docstrings de modulos clave.
- OpenAPI YAML para que coincida con endpoints reales.

No es recomendable renombrar todo el codigo solo para coincidir con el diagrama, porque la estructura actual es razonable para arquitectura hexagonal.

## Frase para defender la implementacion

> El diagrama de componentes representa la arquitectura objetivo del sistema. La implementacion actual materializa un MVP funcional respetando las fronteras principales: SPA separada, API Controller en FastAPI, Analytics Engine como caso de uso, Time Series Repository sobre InfluxDB, IoT Ingestion por MQTT, Broker Mosquitto y External Data Gateway como microservicio. Algunos componentes de la arquitectura objetivo, como Notification Component, Reset Password y Relational Repository sobre PostgreSQL, quedaron postergados o implementados temporalmente con adapters JSON/mock por alcance de entrega.

## Componentes mejor reflejados en el codigo

Los componentes mas fieles a la documentacion son:

- SPA.
- API Controller.
- Security Controller.
- Sign In Controller.
- Analytics Engine, en version MVP.
- IoT Ingestion Component.
- Time Series Repository.
- Broker MQTT.
- External Data Gateway.
- Sensores IoT simulados.

## Componentes que requieren aclaracion

Los componentes que deberian explicarse como pendientes o temporales son:

- Relational Repository.
- PostgreSQL como persistencia real.
- Notification Component.
- Notification Service externo.
- Reset Password Controller.
- Batch Scheduler.
- Catalogo dinamico de reglas.
- Persistencia de alertas y predicciones.

## Recomendacion final para el grupo

No conviene presentar esto como "no respetamos la documentacion". Conviene presentarlo como:

> Tenemos una arquitectura objetivo documentada y una implementacion MVP. El MVP respeta las decisiones arquitectonicas centrales y mantiene puntos de extension claros para completar los componentes postergados.

La clave es mostrar trazabilidad. Si la profesora pregunta por un componente, hay que poder responder:

1. Donde esta implementado.
2. Si esta completo, simplificado o postergado.
3. Por que se tomo esa decision.
4. Como se completaria sin romper la arquitectura.
