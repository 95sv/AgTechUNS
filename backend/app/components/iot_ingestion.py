"""
IoT Ingestion Component
-----------------------
Patrón ETL:
  Extract  → consume mensajes MQTT del broker
  Transform → valida y limpia lecturas (descarta ruido, asigna timestamp)
  Load      → escribe en InfluxDB vía TimeSeriesRepository
"""
import json
import logging
from datetime import datetime

import aiomqtt

from app.config import settings
from app.repositories.timeseries import TimeSeriesRepository

logger = logging.getLogger(__name__)

MQTT_TOPIC = "agtech/sensores/#"

# Rangos válidos para detección de ruido / datos malformados
VALID_RANGES = {
    "temperatura": (-50.0, 80.0),
    "humedad": (0.0, 100.0),
    "ph": (0.0, 14.0),
}


def _validate(field: str, value: float) -> bool:
    lo, hi = VALID_RANGES.get(field, (float("-inf"), float("inf")))
    return lo <= value <= hi


class IoTIngestionService:
    """Servicio que escucha mensajes MQTT y los persiste en InfluxDB."""

    def __init__(self):
        self._ts_repo = TimeSeriesRepository()

    # ── Transform ────────────────────────────────────────────────────────────

    def _parse_and_validate(self, raw: str) -> dict | None:
        """Parsea el payload JSON y valida rangos. Retorna None si el mensaje debe descartarse."""
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            logger.warning("Payload MQTT malformado, descartado: %s", raw[:120])
            return None

        sensor_id = data.get("device_id") or data.get("sensor_id")
        if not sensor_id:
            logger.warning("Mensaje sin device_id, descartado.")
            return None

        payload: dict[str, float | None] = {
            "temperatura": None,
            "humedad": None,
            "ph": None,
        }

        for field in ("temperatura", "humedad", "ph"):
            raw_val = data.get(field)
            if raw_val is None:
                # También acepta formato anidado (uplink_message)
                uplink = data.get("uplink_message", {})
                raw_val = uplink.get(field)
            if raw_val is not None:
                try:
                    val = float(raw_val)
                except (TypeError, ValueError):
                    logger.warning("Valor no numérico para %s: %s, descartado.", field, raw_val)
                    continue
                if _validate(field, val):
                    payload[field] = val
                else:
                    logger.warning("Valor fuera de rango para %s: %s, descartado.", field, val)

        timestamp_str = data.get("timestamp")
        timestamp: datetime | None = None
        if timestamp_str:
            try:
                timestamp = datetime.fromisoformat(timestamp_str)
            except ValueError:
                pass

        return {"sensor_id": sensor_id, "timestamp": timestamp, **payload}

    # ── Extract + Load ────────────────────────────────────────────────────────

    async def start(self) -> None:
        """Bucle principal: suscribe al broker MQTT y procesa mensajes indefinidamente."""
        logger.info(
            "IoT Ingestion: conectando a MQTT %s:%s",
            settings.mqtt_broker_host,
            settings.mqtt_broker_port,
        )
        while True:
            try:
                async with aiomqtt.Client(
                    hostname=settings.mqtt_broker_host,
                    port=settings.mqtt_broker_port,
                ) as client:
                    await client.subscribe(MQTT_TOPIC)
                    logger.info("IoT Ingestion: suscrito a %s", MQTT_TOPIC)
                    async for message in client.messages:
                        await self._handle_message(str(message.payload))
            except aiomqtt.MqttError as exc:
                logger.error("MQTT desconectado: %s — reintentando en 5 s", exc)
                import asyncio
                await asyncio.sleep(5)

    async def _handle_message(self, raw: str) -> None:
        parsed = self._parse_and_validate(raw)
        if parsed is None:
            return

        sensor_id: str = parsed["sensor_id"]
        try:
            await self._ts_repo.write_lectura(
                sensor_id=sensor_id,
                temperatura=parsed["temperatura"],
                humedad=parsed["humedad"],
                ph=parsed["ph"],
                timestamp=parsed["timestamp"],
            )
            logger.debug("Lectura guardada: sensor=%s", sensor_id)
        except Exception as exc:
            logger.error("Error guardando lectura de %s: %s", sensor_id, exc)
