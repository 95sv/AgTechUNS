# app/models.py
from __future__ import annotations

from typing import Literal
from pydantic import BaseModel, Field, confloat, PositiveInt


class WeatherResponse(BaseModel):
    temperature: confloat(strict=True) = Field(..., description="Current temperature (°C)")
    timestamp: str = Field(..., description="ISO timestamp returned by provider")
    latitude: float = Field(..., description="Request latitude")
    longitude: float = Field(..., description="Request longitude")
    provider: Literal["open-meteo"] = Field("open-meteo")


class SatelliteResponse(BaseModel):
    ndvi: confloat(ge=-1.0, le=1.0) = Field(..., description="Normalized Difference Vegetation Index")
    ndmi: confloat(ge=-1.0, le=1.0) = Field(..., description="Normalized Difference Moisture Index")
    parcel_id: PositiveInt = Field(..., description="Identifier for the parcel")
    computed_at: str = Field(..., description="ISO timestamp when indices were computed")
    latency_days: int = Field(5, description="Approximate data latency in days")