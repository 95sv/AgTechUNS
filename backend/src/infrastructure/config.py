"""
Configuración centralizada del backend. Lee de variables de entorno.
"""
from __future__ import annotations
import os
from dataclasses import dataclass

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


@dataclass(frozen=True)
class InfluxSettings:
    url: str
    token: str
    org: str
    bucket: str


@dataclass(frozen=True)
class MqttSettings:
    host: str
    port: int
    topic_subscribe: str


@dataclass(frozen=True)
class ExternalGatewaySettings:
    url: str


influx_settings = InfluxSettings(
    url=os.getenv("INFLUXDB_URL", "http://localhost:8086"),
    token=os.getenv("INFLUXDB_TOKEN", "agtech-dev-token-cambiar-en-prod"),
    org=os.getenv("INFLUXDB_ORG", "agtech-uns"),
    bucket=os.getenv("INFLUXDB_BUCKET", "agtech_data"),
)

mqtt_settings = MqttSettings(
    host=os.getenv("MQTT_HOST", "localhost"),
    port=int(os.getenv("MQTT_PORT", "1883")),
    topic_subscribe=os.getenv("MQTT_TOPIC_SUBSCRIBE", "agtech/sensores/+"),
)

gateway_settings = ExternalGatewaySettings(
    url=os.getenv("EXTERNAL_GATEWAY_URL", "http://localhost:8001"),
)

# JWT — fuente única de verdad para token de autenticación
JWT_SECRET: str = os.getenv("JWT_SECRET", "agtech-dev-secret-cambiar-en-prod")
JWT_ALGORITHM: str = "HS256"
JWT_EXPIRE_MINUTES: int = 60
