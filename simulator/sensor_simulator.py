"""
Sensor IoT simulado de AgTechUNS.

Publica lecturas sintéticas en el broker MQTT con la frecuencia configurada,
emulando el comportamiento de sensores físicos en parcelas reales.
"""
from __future__ import annotations
import argparse
import asyncio
import json
import os
import random
from datetime import datetime, timezone

import aiomqtt

MAPEO_SENSOR_PARCELA = {
    "SN-001": "Parcela-Norte",
    "SN-002": "Parcela-Sur",
    "SN-003": "Parcela-Este",
}

MQTT_HOST = os.getenv("MQTT_HOST", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
TOPIC_PREFIX = os.getenv("MQTT_TOPIC_PREFIX", "agtech/sensores")


def generar_lectura(nombre_codigo_sensor: str) -> dict:
    return {
        "nombre_codigo_sensor": nombre_codigo_sensor,
        "nombre_parcela": MAPEO_SENSOR_PARCELA.get(nombre_codigo_sensor, "Parcela-Desconocida"),
        "valor_temperatura": round(random.uniform(12.0, 35.0), 1),
        "valor_humedad": round(random.uniform(20.0, 90.0), 1),
        "fecha_hora": datetime.now(timezone.utc).isoformat(),
    }


async def publicar_sensor(nombre: str, intervalo: float) -> None:
    topic = f"{TOPIC_PREFIX}/{nombre}"
    async with aiomqtt.Client(hostname=MQTT_HOST, port=MQTT_PORT) as client:
        print(f"[{nombre}] publicando en {topic} cada {intervalo}s")
        while True:
            lectura = generar_lectura(nombre)
            await client.publish(topic, payload=json.dumps(lectura))
            print(f"[{nombre}] T={lectura['valor_temperatura']}°C  H={lectura['valor_humedad']}%")
            await asyncio.sleep(intervalo)


async def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sensores", nargs="+", default=["SN-001", "SN-002"])
    parser.add_argument("--intervalo", type=float, default=3.0)
    args = parser.parse_args()
    await asyncio.gather(*(publicar_sensor(s, args.intervalo) for s in args.sensores))


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nSimulador detenido.")
