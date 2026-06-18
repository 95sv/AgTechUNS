"""
Router HTTP de gestión de Parcelas (CRUD).
"""
from fastapi import APIRouter, Depends, HTTPException, status

from src.domain.entities.parcela import Parcela
from src.infrastructure.persistence.json_parcela_repository import (
    JsonParcelaRepository, ParcelaYaExiste, ParcelaNoEncontrada,
)
from src.interfaces.http.auth_dependency import require_admin
from src.interfaces.http.dependencies import get_parcela_repo

router = APIRouter(prefix="/parcelas", tags=["Gestión: Parcelas"])


@router.get("")
async def listar(repo: JsonParcelaRepository = Depends(get_parcela_repo)) -> dict:
    parcelas = await repo.listar()
    return {"parcelas": [p.model_dump() for p in parcelas]}


@router.post("", status_code=status.HTTP_201_CREATED)
async def crear(
    parcela: Parcela,
    repo: JsonParcelaRepository = Depends(get_parcela_repo),
    _: dict = Depends(require_admin),
) -> Parcela:
    try:
        return await repo.crear(parcela)
    except ParcelaYaExiste as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))


@router.delete("/{nombre_parcela}", status_code=status.HTTP_204_NO_CONTENT, response_model=None)
async def eliminar(
    nombre_parcela: str,
    repo: JsonParcelaRepository = Depends(get_parcela_repo),
    _: dict = Depends(require_admin),
) -> None:
    try:
        await repo.eliminar(nombre_parcela)
    except ParcelaNoEncontrada:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Parcela no encontrada")
