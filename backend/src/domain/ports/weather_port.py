"""
Puerto secundario para el servicio de clima. Lo implementa el cliente HTTP
del External Data Gateway.
"""
from __future__ import annotations
from typing import Protocol


class WeatherPort(Protocol):
    async def fetch_weather(self, lat: float, lon: float) -> dict: ...
