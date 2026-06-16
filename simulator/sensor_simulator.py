"""
Sensor IoT simulado de AgTechUNS.

Lee la lista de parcelas (y sus sensores) desde el archivo de configuración
que el backend también usa. De esa forma, agregar una parcela nueva consiste
en editar config/parcelas.json y reiniciar dos servicios.
"""
from __future__ import annotations
import asyncio
import json
import os
import random
from datetime import datetime, timezone
from pathlib import Path

import aiomqtt

MQTT_HOST = os.getenv("MQTT_HOST", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
TOPIC_PREFIX = os.getenv("MQTT_TOPIC_PREFIX", "agtech/sensores")
INTERVALO = float(os.getenv("INTERVALO", "3.0"))
CONFIG_PATH = Path(os.getenv("PARCELAS_CONFIG_PATH", "/app/config/parcelas.json"))

PARCELAS_FALLBACK = [
    {"nombre_parcela": "Parcela-Norte", "nombre_codigo_sensor": "SN-001"},
    {"nombre_parcela": "Parcela-Sur",   "nombre_codigo_sensor": "SN-002"},
]


def cargar_parcelas() -> list[dict]:
    if not CONFIG_PATH.exists():
        print(f"[!] {CONFIG_PATH} no encontrado, usando fallback")
        return PARCELAS_FALLBACK
    with CONFIG_PATH.open(encoding="utf-8") as f:
        return json.load(f)["parcelas"]


def generar_lectura(parcela: dict) -> dict:
    return {
        "nombre_codigo_sensor": parcela["nombre_codigo_sensor"],
        "nombre_parcela": parcela["nombre_parcela"],
        "valor_temperatura": round(random.uniform(12.0, 35.0), 1),
        "valor_humedad": round(random.uniform(20.0, 90.0), 1),
        "fecha_hora": datetime.now(timezone.utc).isoformat(),
    }


async def publicar_sensor(parcela: dict, intervalo: float) -> None:
    sensor = parcela["nombre_codigo_sensor"]
    topic = f"{TOPIC_PREFIX}/{sensor}"
    async with aiomqtt.Client(hostname=MQTT_HOST, port=MQTT_PORT) as client:
        print(f"[{sensor}] publicando en {topic} cada {intervalo}s")
        while True:
            lectura = generar_lectura(parcela)
            await client.publish(topic, payload=json.dumps(lectura))
            print(f"[{sensor}] T={lectura['valor_temperatura']}°C  H={lectura['valor_humedad']}%")
            await asyncio.sleep(intervalo)


async def main() -> None:
    parcelas = cargar_parcelas()
    if not parcelas:
        print("Sin parcelas para simular. Saliendo.")
        return
    print(f"Simulando {len(parcelas)} sensor(es): {[p['nombre_codigo_sensor'] for p in parcelas]}")
    await asyncio.gather(*(publicar_sensor(p, INTERVALO) for p in parcelas))


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nSimulador detenido.")
