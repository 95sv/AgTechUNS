"""
Adapter secundario: cliente HTTP del External Data Gateway.

Materializa la Capa Anticorrupción del lado consumidor: el backend habla
con este cliente como si fuera un servicio interno, sin saber que detrás
hay un microservicio FastAPI que a su vez habla con Open-Meteo y GEE.
"""
from __future__ import annotations
import httpx

from src.infrastructure.config import ExternalGatewaySettings, gateway_settings


class ExternalGatewayUnavailable(RuntimeError):
    pass


class ExternalGatewayClient:
    def __init__(self, settings: ExternalGatewaySettings = gateway_settings):
        self._base_url = settings.url

    async def fetch_weather(self, lat: float, lon: float) -> dict:
        async with httpx.AsyncClient(timeout=httpx.Timeout(15.0)) as c:
            try:
                resp = await c.get(f"{self._base_url}/weather", params={"lat": lat, "lon": lon})
                resp.raise_for_status()
                return resp.json()
            except httpx.HTTPError as exc:
                raise ExternalGatewayUnavailable(f"Gateway clima falló: {exc}") from exc
