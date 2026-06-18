"""
Entidad Parcela — unidad de cultivo monitorizada por un sensor.
Ahora incluye nombre_campo: cada parcela pertenece a un Campo.
"""
from pydantic import BaseModel, Field


class Parcela(BaseModel):
    nombre_parcela: str = Field(..., min_length=1)
    nombre_campo: str = Field(default="", description="FK conceptual a Campo")
    nombre_codigo_sensor: str = Field(..., min_length=1)
    lat: float = Field(..., ge=-90, le=90)
    lon: float = Field(..., ge=-180, le=180)
