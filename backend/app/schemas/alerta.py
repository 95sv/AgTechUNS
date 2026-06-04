from datetime import datetime
from pydantic import BaseModel


class AlertaResponse(BaseModel):
    id_alerta: int
    fecha_emision: datetime
    mensaje: str
    nombre_parcela: str
    email_usuario: str

    model_config = {"from_attributes": True}
