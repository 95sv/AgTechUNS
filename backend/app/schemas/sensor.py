from datetime import datetime
from pydantic import BaseModel, field_validator


class SensorCreate(BaseModel):
    nombre_codigo_sensor: str
    estado: str = "activo"

    @field_validator("nombre_codigo_sensor")
    @classmethod
    def codigo_no_vacio(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("El código del sensor no puede estar vacío")
        return v.strip()


class SensorResponse(BaseModel):
    nombre_codigo_sensor: str
    estado: str

    model_config = {"from_attributes": True}


class AsignarSensorRequest(BaseModel):
    nombre_parcela: str
    nombre_campo: str
    fecha_instalacion: datetime


class LecturaSensor(BaseModel):
    sensor: str
    timestamp: datetime
    temperatura: float | None = None
    humedad: float | None = None
    ph: float | None = None
