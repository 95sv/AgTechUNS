"""
Adapter secundario: implementación del puerto TimeSeriesPort sobre InfluxDB.

ESTE ES EL ÚNICO ARCHIVO DE TODO EL BACKEND QUE CONOCE InfluxDB Y FLUX.
Si mañana se decide migrar a TimescaleDB, solo se reemplaza este archivo
y todo el resto del sistema sigue funcionando sin cambios.
"""
from __future__ import annotations
from typing import Any

from influxdb_client import Point, WritePrecision
from influxdb_client.client.influxdb_client_async import InfluxDBClientAsync

from src.domain.entities.lectura_sensor import LecturaSensor
from src.infrastructure.config import InfluxSettings, influx_settings

MEASUREMENT = "lecturas_sensores"


class InfluxDBRepository:
    def __init__(self, settings: InfluxSettings = influx_settings):
        self._settings = settings
        self._client: InfluxDBClientAsync | None = None

    async def connect(self) -> None:
        self._client = InfluxDBClientAsync(
            url=self._settings.url, token=self._settings.token, org=self._settings.org
        )

    async def close(self) -> None:
        if self._client is not None:
            await self._client.close()
            self._client = None

    def _ensure(self) -> InfluxDBClientAsync:
        if self._client is None:
            raise RuntimeError("InfluxDBRepository no conectado")
        return self._client

    async def guardar_lectura(self, lectura: LecturaSensor) -> None:
        client = self._ensure()
        point = (
            Point(MEASUREMENT)
            .tag("nombre_codigo_sensor", lectura.nombre_codigo_sensor)
            .tag("nombre_parcela", lectura.nombre_parcela)
            .field("valor_temperatura", float(lectura.valor_temperatura))
            .field("valor_humedad", float(lectura.valor_humedad))
            .time(lectura.fecha_hora, WritePrecision.NS)
        )
        await client.write_api().write(bucket=self._settings.bucket, record=point)

    async def ultima_lectura(self, nombre_codigo_sensor: str) -> dict[str, Any] | None:
        client = self._ensure()
        flux = f'''
        from(bucket: "{self._settings.bucket}")
          |> range(start: -24h)
          |> filter(fn: (r) => r["_measurement"] == "{MEASUREMENT}")
          |> filter(fn: (r) => r["nombre_codigo_sensor"] == "{nombre_codigo_sensor}")
          |> last()
        '''
        tables = await client.query_api().query(flux)
        registros: dict[str, Any] = {}
        for table in tables:
            for record in table.records:
                registros["nombre_codigo_sensor"] = record.values.get("nombre_codigo_sensor")
                registros["nombre_parcela"] = record.values.get("nombre_parcela")
                registros[record.get_field()] = record.get_value()
                registros["fecha_hora"] = record.get_time()
        return registros or None

    async def promedio_diario(self, nombre_codigo_sensor: str, campo: str) -> float | None:
        client = self._ensure()
        flux = f'''
        from(bucket: "{self._settings.bucket}")
          |> range(start: -24h)
          |> filter(fn: (r) => r["_measurement"] == "{MEASUREMENT}")
          |> filter(fn: (r) => r["nombre_codigo_sensor"] == "{nombre_codigo_sensor}")
          |> filter(fn: (r) => r["_field"] == "{campo}")
          |> mean()
        '''
        tables = await client.query_api().query(flux)
        for table in tables:
            for record in table.records:
                return float(record.get_value())
        return None
