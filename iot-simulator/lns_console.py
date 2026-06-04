"""
LNS Console — Simulador de Red de Sensores IoT
================================================
Simula un LoRaWAN Network Server (LNS) que:
  - Gestiona gateways y sensores por campo
  - Publica lecturas periódicas vía MQTT al tópico agtech/sensores/<device_id>
  - Persiste la configuración en registro_lns.json

Uso: python lns_console.py
"""

import json
import os
import random
import threading
import time
from datetime import datetime, timezone

import paho.mqtt.client as mqtt

# ── Configuración ──────────────────────────────────────────────────────────
MQTT_HOST = os.getenv("MQTT_BROKER_HOST", "localhost")
MQTT_PORT = int(os.getenv("MQTT_BROKER_PORT", "1883"))
TOPIC_PREFIX = "agtech/sensores"
REGISTRO_FILE = "registro_lns.json"
TRANSMIT_INTERVAL = 10  # segundos entre lecturas

# Rangos realistas de valores simulados por tipo de cultivo
SENSOR_PROFILES = {
    "default":    {"temp": (15.0, 35.0), "hum": (30.0, 80.0), "ph": (6.0, 7.5)},
    "cereal":     {"temp": (10.0, 30.0), "hum": (40.0, 70.0), "ph": (6.0, 7.0)},
    "frutilla":   {"temp": (18.0, 28.0), "hum": (60.0, 90.0), "ph": (5.5, 6.5)},
    "soja":       {"temp": (20.0, 35.0), "hum": (35.0, 75.0), "ph": (6.0, 7.0)},
    "vid":        {"temp": (15.0, 38.0), "hum": (25.0, 60.0), "ph": (5.5, 7.0)},
}


# ── Persistencia ──────────────────────────────────────────────────────────

def cargar_registro() -> dict:
    if os.path.exists(REGISTRO_FILE):
        with open(REGISTRO_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"campos": {}}


def guardar_registro(reg: dict) -> None:
    with open(REGISTRO_FILE, "w", encoding="utf-8") as f:
        json.dump(reg, f, indent=2, ensure_ascii=False)


# ── MQTT ──────────────────────────────────────────────────────────────────

def crear_cliente_mqtt() -> mqtt.Client:
    client = mqtt.Client(client_id="lns_console", protocol=mqtt.MQTTv5)
    client.on_connect = lambda c, u, f, rc, p: print(
        f"  [MQTT] Conectado al broker {MQTT_HOST}:{MQTT_PORT} (rc={rc})"
    )
    client.on_disconnect = lambda c, u, rc, p=None: print(f"  [MQTT] Desconectado (rc={rc})")
    return client


# ── Simulación de lecturas ────────────────────────────────────────────────

def _generar_lectura(sensor: dict) -> dict:
    perfil = SENSOR_PROFILES.get(sensor.get("perfil", "default"), SENSOR_PROFILES["default"])
    temp = round(random.uniform(*perfil["temp"]) + random.gauss(0, 0.5), 2)
    hum = round(random.uniform(*perfil["hum"]) + random.gauss(0, 1.0), 2)
    ph = round(random.uniform(*perfil["ph"]) + random.gauss(0, 0.05), 2)
    return {
        "device_id": sensor["dev_eui"],
        "campo_id": sensor["campo_id"],
        "parcela_id": sensor.get("parcela_id", ""),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "temperatura": temp,
        "humedad": hum,
        "ph": ph,
        "rssi": random.randint(-110, -60),
    }


def _loop_transmision(registro: dict, stop_event: threading.Event, mqtt_client: mqtt.Client) -> None:
    while not stop_event.is_set():
        for campo_id, campo in registro["campos"].items():
            sensores = campo.get("sensores", [])
            gateways = campo.get("gateways", [])
            if not gateways:
                print(f"  [WARN] Campo '{campo_id}' sin gateways — sensores sin cobertura.")
                continue
            for sensor in sensores:
                lectura = _generar_lectura(sensor)
                topic = f"{TOPIC_PREFIX}/{sensor['dev_eui']}"
                payload = json.dumps(lectura)
                mqtt_client.publish(topic, payload, qos=1)
                print(
                    f"  [TX] {sensor['dev_eui']} → temp={lectura['temperatura']}°C "
                    f"hum={lectura['humedad']}% ph={lectura['ph']}"
                )
        stop_event.wait(TRANSMIT_INTERVAL)


# ── Menú ──────────────────────────────────────────────────────────────────

def _input(prompt: str) -> str:
    return input(prompt).strip()


def menu_campo(registro: dict, campo_id: str, stop_event: threading.Event) -> None:
    campo = registro["campos"][campo_id]
    while True:
        estado = "▶ EN TRANSMISIÓN" if not stop_event.is_set() else "⏹ DETENIDO"
        print(f"\n── Campo: {campo_id} [{estado}] ──")
        print("1. Listar gateways y sensores")
        print("2. Registrar nueva gateway")
        print("3. Registrar nuevo sensor")
        print("4. Eliminar gateway")
        print("5. Eliminar sensor")
        print("6. Volver")
        op = _input("Opción: ")

        if op == "1":
            print(f"\n  Gateways ({len(campo['gateways'])}):")
            for gw in campo["gateways"]:
                print(f"    - {gw['gateway_id']} | ubicacion: {gw.get('ubicacion', 'N/A')}")
            print(f"\n  Sensores ({len(campo['sensores'])}):")
            for s in campo["sensores"]:
                print(f"    - {s['dev_eui']} | parcela: {s.get('parcela_id', 'N/A')} | perfil: {s.get('perfil', 'default')}")
            if not campo["gateways"] and campo["sensores"]:
                print("  ⚠ Hay sensores sin cobertura (no hay gateways registradas)")

        elif op == "2":
            gw_id = _input("  ID de gateway (ej: gw-norte-01): ")
            ubicacion = _input("  Ubicación (ej: Mástil norte): ")
            campo["gateways"].append({"gateway_id": gw_id, "ubicacion": ubicacion, "campo_id": campo_id})
            guardar_registro(registro)
            print(f"  Gateway '{gw_id}' registrada.")

        elif op == "3":
            dev_eui = _input("  DevEUI del sensor (ej: SN-001): ")
            parcela_id = _input("  Parcela asignada (ej: parcela-norte): ")
            perfil = _input(f"  Perfil de cultivo {list(SENSOR_PROFILES.keys())} [default]: ") or "default"
            if perfil not in SENSOR_PROFILES:
                perfil = "default"
            campo["sensores"].append({
                "dev_eui": dev_eui,
                "campo_id": campo_id,
                "parcela_id": parcela_id,
                "perfil": perfil,
            })
            guardar_registro(registro)
            print(f"  Sensor '{dev_eui}' registrado en parcela '{parcela_id}'.")

        elif op == "4":
            if not campo["gateways"]:
                print("  No hay gateways registradas.")
            else:
                for i, gw in enumerate(campo["gateways"]):
                    print(f"  {i+1}. {gw['gateway_id']}")
                idx = _input("  Número a eliminar: ")
                try:
                    campo["gateways"].pop(int(idx) - 1)
                    guardar_registro(registro)
                    print("  Gateway eliminada.")
                except (ValueError, IndexError):
                    print("  Selección inválida.")

        elif op == "5":
            if not campo["sensores"]:
                print("  No hay sensores registrados.")
            else:
                for i, s in enumerate(campo["sensores"]):
                    print(f"  {i+1}. {s['dev_eui']} (parcela: {s.get('parcela_id', 'N/A')})")
                idx = _input("  Número a eliminar: ")
                try:
                    campo["sensores"].pop(int(idx) - 1)
                    guardar_registro(registro)
                    print("  Sensor eliminado.")
                except (ValueError, IndexError):
                    print("  Selección inválida.")

        elif op == "6":
            break


def menu_principal(registro: dict, stop_event: threading.Event, mqtt_client: mqtt.Client, tx_thread: list) -> None:
    while True:
        campos = list(registro["campos"].keys())
        estado = "▶ EN TRANSMISIÓN" if (tx_thread and tx_thread[0].is_alive()) else "⏹ DETENIDO"
        print(f"\n══════════════════════════════════")
        print(f" AgTechUNS — LNS Console [{estado}]")
        print(f"══════════════════════════════════")
        print("1. Gestionar campo")
        print("2. Crear nuevo campo")
        print("3. Iniciar transmisión")
        print("4. Detener transmisión")
        print("5. Mostrar últimas configuraciones")
        print("6. Salir")
        op = _input("Opción: ")

        if op == "1":
            if not campos:
                print("  No hay campos registrados. Cree uno primero.")
            else:
                print("  Campos disponibles:")
                for i, c in enumerate(campos):
                    print(f"    {i+1}. {c}")
                idx = _input("  Seleccionar campo (número): ")
                try:
                    campo_id = campos[int(idx) - 1]
                    menu_campo(registro, campo_id, stop_event)
                except (ValueError, IndexError):
                    print("  Selección inválida.")

        elif op == "2":
            campo_id = _input("  Nombre/ID del campo: ")
            if campo_id in registro["campos"]:
                print("  Ya existe un campo con ese nombre.")
            else:
                registro["campos"][campo_id] = {"gateways": [], "sensores": []}
                guardar_registro(registro)
                print(f"  Campo '{campo_id}' creado.")

        elif op == "3":
            if tx_thread and tx_thread[0].is_alive():
                print("  La transmisión ya está activa.")
            else:
                total_sensores = sum(len(c["sensores"]) for c in registro["campos"].values())
                if total_sensores == 0:
                    print("  No hay sensores registrados. Registre al menos uno antes de iniciar.")
                else:
                    stop_event.clear()
                    t = threading.Thread(
                        target=_loop_transmision,
                        args=(registro, stop_event, mqtt_client),
                        daemon=True,
                    )
                    tx_thread.clear()
                    tx_thread.append(t)
                    t.start()
                    print(f"  Transmisión iniciada — {total_sensores} sensor(es) cada {TRANSMIT_INTERVAL}s.")

        elif op == "4":
            stop_event.set()
            print("  Transmisión detenida.")

        elif op == "5":
            for campo_id, campo in registro["campos"].items():
                print(f"\n  Campo: {campo_id}")
                print(f"    Gateways: {[gw['gateway_id'] for gw in campo['gateways']]}")
                print(f"    Sensores: {[s['dev_eui'] for s in campo['sensores']]}")

        elif op == "6":
            stop_event.set()
            print("  Saliendo del LNS Console.")
            break


# ── Punto de entrada ──────────────────────────────────────────────────────

def main() -> None:
    print("Iniciando AgTechUNS LNS Console...")
    registro = cargar_registro()

    mqtt_client = crear_cliente_mqtt()
    try:
        mqtt_client.connect(MQTT_HOST, MQTT_PORT, keepalive=60)
        mqtt_client.loop_start()
    except Exception as e:
        print(f"  [WARN] No se pudo conectar al broker MQTT ({e}). Modo offline.")

    stop_event = threading.Event()
    stop_event.set()
    tx_thread: list = []

    try:
        menu_principal(registro, stop_event, mqtt_client, tx_thread)
    except KeyboardInterrupt:
        print("\n  Interrumpido por el usuario.")
    finally:
        stop_event.set()
        mqtt_client.loop_stop()
        mqtt_client.disconnect()


if __name__ == "__main__":
    main()
