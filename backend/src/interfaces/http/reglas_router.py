"""
Router de Reglas Agroclimáticas — CU-07.

Permite configurar umbrales dinámicos para el pipeline de alertas.
MVP: persiste en memoria (las reglas hardcodeadas están en reglas_agronomicas.py).
"""
from fastapi import APIRouter, Depends, status
from pydantic import BaseModel

from src.interfaces.http.auth_dependency import require_admin

router = APIRouter(prefix="/reglas", tags=["Catálogos y Configuración"])

_reglas_custom: list[dict] = []


class Regla(BaseModel):
    metrica: str
    operador: str
    valor: float


@router.get("")
async def listar_reglas() -> dict:
    return {"data": _reglas_custom, "pagination": {"page": 1, "limit": 20, "total": len(_reglas_custom), "total_pages": 1}}


@router.post("", status_code=status.HTTP_201_CREATED)
async def crear_regla(
    regla: Regla,
    _: dict = Depends(require_admin),
) -> dict:
    nueva = regla.model_dump()
    _reglas_custom.append(nueva)
    return nueva
