"""
Entidad LecturaSensor — representa una medición de un sensor IoT.
Pertenece a la CAPA DE DOMINIO: no depende de FastAPI ni InfluxDB.
"""
from __future__ import annotations
from datetime import datetime, timezone
from pydantic import BaseModel, Field, field_validator


class LecturaSensor(BaseModel):
    nombre_codigo_sensor: str = Field(..., min_length=1)
    nombre_parcela: str = Field(..., min_length=1)
    valor_temperatura: float
    valor_humedad: float = Field(..., ge=0, le=100)
    fecha_hora: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @field_validator("valor_temperatura")
    @classmethod
    def temperatura_en_rango_logico(cls, v: float) -> float:
        if not -50.0 <= v <= 70.0:
            raise ValueError(f"Temperatura fuera de rango lógico: {v}")
        return v
