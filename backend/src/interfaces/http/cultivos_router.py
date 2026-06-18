"""
Router HTTP de gestión de variedades de Cultivo (catálogo).
"""
from fastapi import APIRouter, Depends, HTTPException, status

from src.domain.entities.cultivo import Cultivo
from src.infrastructure.persistence.json_cultivo_repository import (
    JsonCultivoRepository, CultivoYaExiste, CultivoNoEncontrado,
)
from src.interfaces.http.auth_dependency import require_admin
from src.interfaces.http.dependencies import get_cultivo_repo

router = APIRouter(prefix="/cultivos", tags=["Gestión: Cultivos"])


@router.get("")
async def listar(repo: JsonCultivoRepository = Depends(get_cultivo_repo)) -> dict:
    cultivos = await repo.listar()
    return {"cultivos": [c.model_dump() for c in cultivos]}


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


@router.delete("/{nombre}/{variedad}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar(
    nombre: str,
    variedad: str,
    repo: JsonCultivoRepository = Depends(get_cultivo_repo),
    _: dict = Depends(require_admin),
) -> None:
    try:
        await repo.eliminar(nombre, variedad)
    except CultivoNoEncontrado:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Variedad no encontrada")
