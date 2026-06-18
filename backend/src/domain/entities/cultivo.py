"""
Entidad Cultivo — catálogo de variedades disponibles para sembrar.
La PK conceptual es nombre_cultivo (+ variedad opcional para detalles taxonómicos).
Incluye umbral_humedad_minima para ser usada por el pipeline analítico batch (CU-06).
"""
from pydantic import BaseModel, Field


class Cultivo(BaseModel):
    nombre_cultivo: str = Field(..., min_length=1)
    variedad: str = Field(default="", description="Variedad taxonómica (opcional)")
    umbral_humedad_minima: float = Field(default=30.0, description="Umbral agronómico para pipeline batch")

    @property
    def clave(self) -> str:
        return f"{self.nombre_cultivo}::{self.variedad}" if self.variedad else self.nombre_cultivo
