"""
Router de Integraciones Externas — proxy hacia el External Data Gateway.

Expone los endpoints del contrato YAML Entrega 4:
  GET /external/weather?lat=...&lon=...        → datos meteorológicos (Open-Meteo)
  GET /external/satelital?coordenadas=...      → índices satelitales (Google Earth Engine)
"""
from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException, Query

from src.infrastructure.external.gateway_client import (
    ExternalGatewayClient, ExternalGatewayUnavailable,
)
from src.interfaces.http.dependencies import get_weather_client

router = APIRouter(prefix="/external", tags=["Integraciones Externas"])


@router.get("/weather")
async def weather(
    lat: float = Query(..., ge=-90, le=90, description="Latitud"),
    lon: float = Query(..., ge=-180, le=180, description="Longitud"),
    client: ExternalGatewayClient = Depends(get_weather_client),
) -> dict:
    try:
        return await client.fetch_weather(lat, lon)
    except ExternalGatewayUnavailable as exc:
        raise HTTPException(status_code=503, detail=str(exc))


@router.get("/satelital")
async def satelital(
    coordenadas: str = Query(..., description="Polígono o punto de consulta (lat,lon)"),
) -> dict:
    """
    Enriquecimiento satelital vía Google Earth Engine.
    Stub — el gateway real expone /satellite/{parcel_id}.
    Requiere credenciales GEE configuradas en el external-gateway.
    """
    return {
        "mensaje": "Endpoint satelital disponible en el External Data Gateway (/satellite/{parcel_id}).",
        "coordenadas_recibidas": coordenadas,
        "ndvi": None,
        "humedad_suelo_estimada": None,
    }
