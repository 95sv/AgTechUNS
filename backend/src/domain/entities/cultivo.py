"""
Entidad Cultivo — catálogo de variedades disponibles para sembrar.
La PK conceptual es (nombre, variedad).
"""
from pydantic import BaseModel, Field


class Cultivo(BaseModel):
    nombre: str = Field(..., min_length=1)
    variedad: str = Field(..., min_length=1)

    @property
    def clave(self) -> str:
        return f"{self.nombre}::{self.variedad}"
