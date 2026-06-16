"""
Router HTTP del dashboard. Adapter primario que sirve el panel y expone el
endpoint de agregación con el estado actual de las parcelas.

Las parcelas ya no están hardcodeadas: se obtienen del ParcelaRepository.
"""
from fastapi import APIRouter, Depends

from src.infrastructure.persistence.influxdb_repository import InfluxDBRepository
from src.infrastructure.persistence.json_parcela_repository import JsonParcelaRepository
from src.infrastructure.external.gateway_client import (
    ExternalGatewayClient,
    ExternalGatewayUnavailable,
)
from src.interfaces.http.dependencies import (
    get_time_series_repo,
    get_weather_client,
    get_parcela_repo,
)

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/parcelas")
async def listar_parcelas_con_estado(
    ts: InfluxDBRepository = Depends(get_time_series_repo),
    w: ExternalGatewayClient = Depends(get_weather_client),
    parcelas_repo: JsonParcelaRepository = Depends(get_parcela_repo),
) -> dict:
    """Devuelve cada parcela con su última lectura del sensor y el clima actual."""
    parcelas = await parcelas_repo.listar()
    resultados = []
    for p in parcelas:
        item = p.model_dump()
        try:
            item["ultima_lectura"] = await ts.ultima_lectura(p.nombre_codigo_sensor)
        except Exception:
            item["ultima_lectura"] = None
        try:
            item["clima_actual"] = await w.fetch_weather(p.lat, p.lon)
        except ExternalGatewayUnavailable:
            item["clima_actual"] = None
        resultados.append(item)
    return {"parcelas": resultados}
