"""
External Data Gateway
---------------------
Centraliza las peticiones a sistemas externos:
  - Open-Meteo API (pronóstico meteorológico)
  - Google Earth Engine (imágenes satelitales NDVI/NDMI) — stub simulado

Responsabilidades: solo realiza el fetch y normaliza la respuesta.
No persiste datos (eso lo hace el Analytics Engine o el API Controller).
"""
import logging
from datetime import datetime

import httpx

from app.config import settings

logger = logging.getLogger(__name__)


class ExternalDataGateway:

    # ── Open-Meteo ────────────────────────────────────────────────────────────

    async def get_pronostico(self, lat: float, lon: float, dias: int = 7) -> dict | None:
        """
        Obtiene pronóstico meteorológico de Open-Meteo para las coordenadas dadas.
        Devuelve temperatura_max, temperatura_min, precipitacion_mm por día.
        """
        params = {
            "latitude": lat,
            "longitude": lon,
            "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum",
            "forecast_days": dias,
            "timezone": "America/Argentina/Buenos_Aires",
        }
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(settings.weather_api_url, params=params)
                resp.raise_for_status()
                raw = resp.json()
        except Exception as exc:
            logger.error("Error consultando Open-Meteo: %s", exc)
            return None

        daily = raw.get("daily", {})
        fechas = daily.get("time", [])
        temp_max = daily.get("temperature_2m_max", [])
        temp_min = daily.get("temperature_2m_min", [])
        precip = daily.get("precipitation_sum", [])

        return {
            "fuente": "Open-Meteo",
            "lat": lat,
            "lon": lon,
            "pronostico": [
                {
                    "fecha": fechas[i] if i < len(fechas) else None,
                    "temperatura_max": temp_max[i] if i < len(temp_max) else None,
                    "temperatura_min": temp_min[i] if i < len(temp_min) else None,
                    "precipitacion_mm": precip[i] if i < len(precip) else None,
                }
                for i in range(len(fechas))
            ],
        }

    # ── Google Earth Engine (stub simulado) ──────────────────────────────────

    async def get_indices_satelitales(
        self, nombre_parcela: str, lat: float, lon: float
    ) -> dict | None:
        """
        Obtiene índices NDVI y NDMI para la parcela.
        En el alcance del proyecto los sensores son simulados, por lo que
        este método devuelve valores simulados realistas para desarrollo.
        En producción se integraría con Google Earth Engine via ee.Initialize().
        """
        import random
        import math

        random.seed(hash(nombre_parcela + datetime.utcnow().strftime("%Y%m%d")))
        ndvi = round(random.uniform(0.3, 0.75), 4)
        ndmi = round(random.uniform(0.1, 0.55), 4)

        logger.info(
            "Índices satelitales (simulados) para parcela=%s: NDVI=%.4f NDMI=%.4f",
            nombre_parcela, ndvi, ndmi,
        )

        return {
            "fuente": "GEE (simulado)",
            "parcela": nombre_parcela,
            "fecha_captura": datetime.utcnow().isoformat(),
            "ndvi": ndvi,
            "ndmi": ndmi,
            "interpretacion_ndvi": _interpretar_ndvi(ndvi),
            "interpretacion_ndmi": _interpretar_ndmi(ndmi),
        }


def _interpretar_ndvi(ndvi: float) -> str:
    if ndvi >= 0.6:
        return "Vegetación densa y saludable"
    if ndvi >= 0.2:
        return "Vegetación escasa o en estrés"
    return "Suelo desnudo, agua o nieve"


def _interpretar_ndmi(ndmi: float) -> str:
    if ndmi >= 0.4:
        return "Alta humedad, vegetación sin estrés hídrico"
    if ndmi >= 0.2:
        return "Cobertura media-alta, humedad adecuada"
    if ndmi >= 0.0:
        return "Cobertura media, estrés hídrico moderado"
    return "Estrés hídrico alto o suelo desnudo"
