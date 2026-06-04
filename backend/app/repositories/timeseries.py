from datetime import datetime, timedelta
from influxdb_client.client.influxdb_client_async import InfluxDBClientAsync
from app.config import settings


class TimeSeriesRepository:
    """Acceso a InfluxDB para lecturas de sensores (serie temporal)."""

    def __init__(self):
        self._url = settings.influxdb_url
        self._token = settings.influxdb_token
        self._org = settings.influxdb_org
        self._bucket = settings.influxdb_bucket

    async def write_lectura(
        self,
        sensor_id: str,
        temperatura: float | None,
        humedad: float | None,
        ph: float | None,
        timestamp: datetime | None = None,
    ) -> None:
        ts = timestamp or datetime.utcnow()
        fields: dict[str, float] = {}
        if temperatura is not None:
            fields["valor_temperatura"] = temperatura
        if humedad is not None:
            fields["valor_humedad"] = humedad
        if ph is not None:
            fields["valor_ph"] = ph

        if not fields:
            return

        line = (
            f"lecturas_sensores,nombre_codigo_sensor={sensor_id} "
            + ",".join(f"{k}={v}" for k, v in fields.items())
            + f" {int(ts.timestamp() * 1_000_000_000)}"
        )

        async with InfluxDBClientAsync(
            url=self._url, token=self._token, org=self._org
        ) as client:
            write_api = client.write_api()
            await write_api.write(bucket=self._bucket, record=line)

    async def get_ultima_lectura(self, sensor_id: str) -> dict | None:
        query = f"""
        from(bucket: "{self._bucket}")
          |> range(start: -24h)
          |> filter(fn: (r) => r["_measurement"] == "lecturas_sensores")
          |> filter(fn: (r) => r["nombre_codigo_sensor"] == "{sensor_id}")
          |> last()
          |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
        """
        async with InfluxDBClientAsync(
            url=self._url, token=self._token, org=self._org
        ) as client:
            query_api = client.query_api()
            tables = await query_api.query(query)
            for table in tables:
                for record in table.records:
                    return {
                        "timestamp": record.get_time(),
                        "sensor": sensor_id,
                        "temperatura": record.values.get("valor_temperatura"),
                        "humedad": record.values.get("valor_humedad"),
                        "ph": record.values.get("valor_ph"),
                    }
        return None

    async def get_lecturas_parcela(
        self,
        sensor_ids: list[str],
        horas: int = 24,
    ) -> list[dict]:
        if not sensor_ids:
            return []

        sensor_filter = " or ".join(
            f'r["nombre_codigo_sensor"] == "{s}"' for s in sensor_ids
        )
        query = f"""
        from(bucket: "{self._bucket}")
          |> range(start: -{horas}h)
          |> filter(fn: (r) => r["_measurement"] == "lecturas_sensores")
          |> filter(fn: (r) => {sensor_filter})
          |> pivot(rowKey:["_time","nombre_codigo_sensor"], columnKey: ["_field"], valueColumn: "_value")
        """
        results = []
        async with InfluxDBClientAsync(
            url=self._url, token=self._token, org=self._org
        ) as client:
            query_api = client.query_api()
            tables = await query_api.query(query)
            for table in tables:
                for record in table.records:
                    results.append({
                        "timestamp": record.get_time(),
                        "sensor": record.values.get("nombre_codigo_sensor"),
                        "temperatura": record.values.get("valor_temperatura"),
                        "humedad": record.values.get("valor_humedad"),
                        "ph": record.values.get("valor_ph"),
                    })
        return results

    async def get_promedios_diarios(
        self,
        sensor_ids: list[str],
        horas: int = 24,
    ) -> dict[str, dict]:
        """Devuelve promedios de temperatura y humedad por sensor (usado por el Analytics Engine)."""
        if not sensor_ids:
            return {}

        sensor_filter = " or ".join(
            f'r["nombre_codigo_sensor"] == "{s}"' for s in sensor_ids
        )
        query = f"""
        from(bucket: "{self._bucket}")
          |> range(start: -{horas}h)
          |> filter(fn: (r) => r["_measurement"] == "lecturas_sensores")
          |> filter(fn: (r) => {sensor_filter})
          |> group(columns: ["nombre_codigo_sensor", "_field"])
          |> mean()
        """
        promedios: dict[str, dict] = {}
        async with InfluxDBClientAsync(
            url=self._url, token=self._token, org=self._org
        ) as client:
            query_api = client.query_api()
            tables = await query_api.query(query)
            for table in tables:
                for record in table.records:
                    sensor = record.values.get("nombre_codigo_sensor")
                    campo = record.get_field()
                    valor = record.get_value()
                    if sensor not in promedios:
                        promedios[sensor] = {}
                    promedios[sensor][campo] = valor
        return promedios
