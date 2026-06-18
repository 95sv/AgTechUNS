"""
Router HTTP de gestión de Campos. Operaciones de escritura protegidas por rol admin.
"""
from fastapi import APIRouter, Depends, HTTPException, status

from src.domain.entities.campo import Campo
from src.infrastructure.persistence.json_campo_repository import (
    JsonCampoRepository, CampoYaExiste, CampoNoEncontrado,
)
from src.interfaces.http.auth_dependency import require_admin
from src.interfaces.http.dependencies import get_campo_repo

router = APIRouter(prefix="/campos", tags=["Gestión: Campos"])


@router.get("")
async def listar(repo: JsonCampoRepository = Depends(get_campo_repo)) -> dict:
    campos = await repo.listar()
    return {"campos": [c.model_dump() for c in campos]}


@router.post("", status_code=status.HTTP_201_CREATED)
async def crear(
    campo: Campo,
    repo: JsonCampoRepository = Depends(get_campo_repo),
    _: dict = Depends(require_admin),
) -> Campo:
    try:
        return await repo.crear(campo)
    except CampoYaExiste:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Campo ya existe")


@router.delete("/{nombre_campo}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar(
    nombre_campo: str,
    repo: JsonCampoRepository = Depends(get_campo_repo),
    _: dict = Depends(require_admin),
) -> None:
    try:
        await repo.eliminar(nombre_campo)
    except CampoNoEncontrado:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Campo no encontrado")
