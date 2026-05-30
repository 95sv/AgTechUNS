"""
Adapter primario (driving adapter): consumidor MQTT que invoca al caso de
uso IngestReading por cada mensaje recibido.

Es la "puerta de entrada" no-HTTP del sistema: corre como worker
independiente y trae los datos crudos desde el broker hacia la aplicación.
"""
from __future__ import annotations
import asyncio
import json
import logging

import aiomqtt

from src.application.ingest_reading import IngestReading
from src.infrastructure.config import MqttSettings, mqtt_settings

_log = logging.getLogger("mqtt_consumer")


class MqttConsumer:
    def __init__(self, ingest: IngestReading, settings: MqttSettings = mqtt_settings):
        self._ingest = ingest
        self._settings = settings

    async def run(self) -> None:
        while True:
            try:
                async with aiomqtt.Client(
                    hostname=self._settings.host, port=self._settings.port
                ) as client:
                    await client.subscribe(self._settings.topic_subscribe)
                    _log.info("Suscrito a %s", self._settings.topic_subscribe)
                    async for message in client.messages:
                        try:
                            payload = json.loads(message.payload)
                        except (json.JSONDecodeError, TypeError):
                            _log.error("Payload no JSON descartado")
                            continue
                        await self._ingest.execute(payload)
            except aiomqtt.MqttError as exc:
                _log.warning("Conexión MQTT perdida (%s). Reintento en 5s...", exc)
                await asyncio.sleep(5)
