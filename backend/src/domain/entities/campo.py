"""
Entidad Campo — agrupación lógica de parcelas bajo gestión común.
Capa de dominio.
"""
from pydantic import BaseModel, Field


class Campo(BaseModel):
    nombre_campo: str = Field(..., min_length=1)
    coordenadas_campo: str = Field(..., min_length=1, description="Ubicación o polígono GeoJSON del campo")
    descripcion: str = ""
