"""
Entidad Campo — agrupación lógica de parcelas bajo gestión común.
Capa de dominio.
"""
from pydantic import BaseModel, Field


class Campo(BaseModel):
    nombre_campo: str = Field(..., min_length=1)
    ubicacion: str = Field(..., min_length=1)
    descripcion: str = ""
