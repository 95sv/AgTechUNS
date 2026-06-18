"""
Router HTTP de gestión de Cultivos (catálogo) — CU-09.
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status

from src.domain.entities.cultivo import Cultivo
from src.infrastructure.persistence.json_cultivo_repository import (
    JsonCultivoRepository, CultivoYaExiste, CultivoNoEncontrado,
)
from src.interfaces.http.auth_dependency import require_admin
from src.interfaces.http.dependencies import get_cultivo_repo
from src.interfaces.http._pagination import paginar

router = APIRouter(prefix="/cultivos", tags=["Catálogos y Configuración"])


@router.get("")
async def listar(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    repo: JsonCultivoRepository = Depends(get_cultivo_repo),
) -> dict:
    cultivos = await repo.listar()
    return paginar([c.model_dump() for c in cultivos], page, limit)


@router.post("", status_code=status.HTTP_201_CREATED)
async def crear(
    cultivo: Cultivo,
    repo: JsonCultivoRepository = Depends(get_cultivo_repo),
    _: dict = Depends(require_admin),
) -> Cultivo:
    try:
        return await repo.crear(cultivo)
    except CultivoYaExiste:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Variedad ya existe")


@router.delete("/{nombre_cultivo}", status_code=status.HTTP_204_NO_CONTENT, response_model=None)
async def eliminar(
    nombre_cultivo: str,
    variedad: str = Query(default=""),
    repo: JsonCultivoRepository = Depends(get_cultivo_repo),
    _: dict = Depends(require_admin),
) -> None:
    try:
        await repo.eliminar(nombre_cultivo, variedad)
    except CultivoNoEncontrado:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cultivo no encontrado")
