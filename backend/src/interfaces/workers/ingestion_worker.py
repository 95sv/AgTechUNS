"""
Worker de ingesta IoT. Adapter primario NO-HTTP que mantiene viva la
suscripción MQTT y delega cada mensaje al caso de uso IngestReading.

Corre como proceso independiente (su propio contenedor en docker-compose).
"""
from __future__ import annotations
import asyncio

from src.application.ingest_reading import IngestReading
from src.infrastructure.persistence.influxdb_repository import InfluxDBRepository
from src.infrastructure.messaging.mqtt_consumer import MqttConsumer


async def main() -> None:
    repo = InfluxDBRepository()
    await repo.connect()
    ingest = IngestReading(time_series=repo)
    consumer = MqttConsumer(ingest=ingest)
    try:
        await consumer.run()
    finally:
        await repo.close()


if __name__ == "__main__":
    asyncio.run(main())
