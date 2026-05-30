"""
Caso de uso: Ingestar una lectura cruda de sensor.

Encarna las tres fases del patrón ETL aplicado a la ingesta IoT:
  - Extract:   recibe un dict (payload del broker MQTT) desde el worker.
  - Transform: lo valida con LecturaSensor (descarta lecturas malformadas).
  - Load:      delega la persistencia al puerto TimeSeriesPort.
"""
from __future__ import annotations
import logging
from pydantic import ValidationError

from src.domain.entities.lectura_sensor import LecturaSensor
from src.domain.ports.time_series_port import TimeSeriesPort

_log = logging.getLogger("ingest_reading")


class IngestReading:
    def __init__(self, time_series: TimeSeriesPort):
        self._ts = time_series

    async def execute(self, payload: dict) -> bool:
        """Devuelve True si la lectura fue persistida, False si fue descartada."""
        try:
            lectura = LecturaSensor(**payload)
        except ValidationError as exc:
            _log.error("Lectura inválida descartada: %s | datos=%s", exc.errors(), payload)
            return False
        try:
            await self._ts.guardar_lectura(lectura)
            _log.info(
                "Guardada: %s/%s T=%.1f H=%.1f",
                lectura.nombre_parcela,
                lectura.nombre_codigo_sensor,
                lectura.valor_temperatura,
                lectura.valor_humedad,
            )
            return True
        except Exception as exc:
            _log.error("Error al persistir: %s", exc)
            return False
