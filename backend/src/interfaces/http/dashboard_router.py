"""
Router HTTP del dashboard. Adapter primario que sirve la página estática y
expone un endpoint de agregación con el estado actual de todas las parcelas
(última lectura del sensor + clima ambiente).

Es una vista de lectura: no aplica reglas ni dispara cómputos pesados.
Cuando el usuario quiera evaluar el Analytics Engine, usa /analytics/evaluar.
"""
from fastapi import APIRouter, Depends

from src.infrastructure.persistence.influxdb_repository import InfluxDBRepository
from src.infrastructure.external.gateway_client import (
    ExternalGatewayClient,
    ExternalGatewayUnavailable,
)
from src.interfaces.http.dependencies import (
    get_time_series_repo,
    get_weather_client,
)

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

PARCELAS_DEMO = [
    {"nombre_parcela": "Parcela-Norte", "nombre_codigo_sensor": "SN-001", "lat": -38.71, "lon": -62.27},
    {"nombre_parcela": "Parcela-Sur",   "nombre_codigo_sensor": "SN-002", "lat": -38.75, "lon": -62.30},
]


@router.get("/parcelas")
async def listar_parcelas_con_estado(
    ts: InfluxDBRepository = Depends(get_time_series_repo),
    w: ExternalGatewayClient = Depends(get_weather_client),
) -> dict:
    """
    Devuelve, por cada parcela demo, su última lectura del sensor (InfluxDB)
    y el clima ambiente actual (External Gateway / Open-Meteo).
    Los errores en una de las fuentes no rompen la respuesta global:
    el campo correspondiente queda como null y el dashboard lo refleja.
    """
    resultados = []
    for p in PARCELAS_DEMO:
        item: dict = {**p}
        try:
            item["ultima_lectura"] = await ts.ultima_lectura(p["nombre_codigo_sensor"])
        except Exception:
            item["ultima_lectura"] = None
        try:
            clima = await w.fetch_weather(p["lat"], p["lon"])
            item["clima_actual"] = clima
        except ExternalGatewayUnavailable:
            item["clima_actual"] = None
        resultados.append(item)
    return {"parcelas": resultados}
