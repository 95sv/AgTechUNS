from datetime import datetime
from pydantic import BaseModel


class PrediccionResponse(BaseModel):
    id_prediccion: int
    fecha_emision: datetime
    resultado: str
    fecha_ini: datetime
    fecha_fin: datetime
    nombre_parcela: str

    model_config = {"from_attributes": True}


class EjecucionBatchResponse(BaseModel):
    fecha_ini: datetime
    estado: str
    fecha_fin: datetime | None = None

    model_config = {"from_attributes": True}
