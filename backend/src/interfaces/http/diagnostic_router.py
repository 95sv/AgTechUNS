"""
Router HTTP de diagnóstico. Verifica que el backend está conectado a las
dos fuentes de datos (InfluxDB vía repositorio + clima vía gateway).
"""
from __future__ import annotations
from fastapi import APIRouter, Depends

from src.infrastructure.persistence.influxdb_repository import InfluxDBRepository
from src.infrastructure.external.gateway_client import ExternalGatewayClient, ExternalGatewayUnavailable
from src.interfaces.http.dependencies import get_time_series_repo, get_weather_client

router = APIRouter(prefix="/diagnostico", tags=["Diagnóstico"])


@router.get("/health")
async def health() -> dict:
    return {"status": "ok", "service": "agtech-backend"}


@router.get("/integracion")
async def integracion(
    nombre_codigo_sensor: str = "SN-001",
    lat: float = -38.71,
    lon: float = -62.27,
    ts: InfluxDBRepository = Depends(get_time_series_repo),
    w: ExternalGatewayClient = Depends(get_weather_client),
) -> dict:
    resultado: dict = {}
    try:
        ultima = await ts.ultima_lectura(nombre_codigo_sensor)
        resultado["influxdb"] = {"ok": True, "sensor_consultado": nombre_codigo_sensor, "ultima_lectura": ultima}
    except Exception as exc:
        resultado["influxdb"] = {"ok": False, "error": str(exc)}
    try:
        clima = await w.fetch_weather(lat, lon)
        resultado["external_gateway"] = {"ok": True, "clima_actual": clima}
    except ExternalGatewayUnavailable as exc:
        resultado["external_gateway"] = {"ok": False, "error": str(exc)}
    resultado["stack_ok"] = resultado["influxdb"]["ok"] and resultado["external_gateway"]["ok"]
    return resultado
