"""
Entidad Alerta — generada por el Analytics Engine al disparar una regla agronómica.
"""
from __future__ import annotations
from datetime import datetime, timezone
from typing import Any
from pydantic import BaseModel, Field


class Alerta(BaseModel):
    nombre_parcela: str
    tipo: str
    severidad: str
    mensaje: str
    datos_evaluados: dict[str, Any] = Field(default_factory=dict)
    fecha_generacion: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
