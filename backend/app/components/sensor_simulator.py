"""
Sensor Simulator
----------------
Genera lecturas sintéticas y estables por parcela para desarrollo y demo.

Las lecturas se derivan de la parcela, la fecha y, si existe, del clima
pronosticado para que el resultado sea coherente entre recargas.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
import hashlib
import random


def _clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(maximum, value))


def _hash_seed(text: str) -> int:
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
    return int(digest[:16], 16)


def _first_forecast_item(clima: dict | None) -> dict:
    if not clima:
        return {}
    pronostico = clima.get("pronostico") or []
    if not pronostico:
        return {}
    return pronostico[0] or {}


@dataclass(slots=True)
class SensorSimulator:
    """Genera una lectura sintética por parcela."""

    def simular_parcela(
        self,
        nombre_parcela: str,
        lat: float | None,
        lon: float | None,
        clima: dict | None = None,
        ndvi: float | None = None,
        ndmi: float | None = None,
    ) -> dict:
        forecast = _first_forecast_item(clima)
        fecha_base = date.today().isoformat()
        seed_parts = [nombre_parcela, fecha_base]
        if lat is not None and lon is not None:
            seed_parts.append(f"{lat:.5f}:{lon:.5f}")
        seed = _hash_seed("|".join(seed_parts))
        rng = random.Random(seed)

        temp_max = forecast.get("temperatura_max")
        temp_min = forecast.get("temperatura_min")
        precip = forecast.get("precipitacion_mm") or 0.0
        ndvi_ref = ndvi if ndvi is not None else 0.45
        ndmi_ref = ndmi if ndmi is not None else 0.25

        if temp_max is not None and temp_min is not None:
            temperatura_base = (float(temp_max) + float(temp_min)) / 2
        elif temp_max is not None:
            temperatura_base = float(temp_max) - 2.0
        elif temp_min is not None:
            temperatura_base = float(temp_min) + 2.0
        else:
            temperatura_base = 22.0

        temperatura = _clamp(
            temperatura_base
            + rng.uniform(-1.8, 1.8)
            + (ndvi_ref - 0.45) * 2.2,
            5.0,
            45.0,
        )

        humedad = _clamp(
            82.0
            - temperatura * 1.35
            + float(precip) * 10.0
            + (ndmi_ref - 0.25) * 18.0
            + rng.uniform(-4.0, 4.0),
            18.0,
            98.0,
        )

        ph = _clamp(
            6.35
            + (ndvi_ref - 0.45) * 0.7
            - ((humedad - 60.0) / 180.0)
            + rng.uniform(-0.12, 0.12),
            5.1,
            7.9,
        )

        sensor_id = f"SIM-{nombre_parcela.replace(' ', '-')[:18].upper()}"
        timestamp = datetime.utcnow().isoformat()

        lectura = {
            "sensor": sensor_id,
            "timestamp": timestamp,
            "temperatura": round(temperatura, 1),
            "humedad": round(humedad, 1),
            "ph": round(ph, 1),
            "origen": "simulado",
        }

        return {
            "origen": "simulado",
            "sensores": {sensor_id: lectura},
            "resumen": {
                "temperatura_promedio": lectura["temperatura"],
                "humedad_promedio": lectura["humedad"],
                "ph_promedio": lectura["ph"],
            },
            "timestamp": timestamp,
        }