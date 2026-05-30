"""
Puerto secundario: contrato que cualquier adaptador de series temporales
debe cumplir. La aplicación interactúa con este Protocol, no con InfluxDB
directamente.
"""
from __future__ import annotations
from typing import Any, Protocol

from src.domain.entities.lectura_sensor import LecturaSensor


class TimeSeriesPort(Protocol):
    async def connect(self) -> None: ...
    async def close(self) -> None: ...
    async def guardar_lectura(self, lectura: LecturaSensor) -> None: ...
    async def ultima_lectura(self, nombre_codigo_sensor: str) -> dict[str, Any] | None: ...
    async def promedio_diario(self, nombre_codigo_sensor: str, campo: str) -> float | None: ...
