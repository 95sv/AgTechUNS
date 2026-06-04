from fastapi import APIRouter
from app.api.deps import DB, CurrentUser
from app.repositories import relational as repo
from app.schemas.alerta import AlertaResponse

router = APIRouter()


@router.get("/", response_model=list[AlertaResponse])
async def listar_alertas(db: DB, _: CurrentUser, limit: int = 50):
    return await repo.get_alertas(db, limit=limit)


@router.get("/parcela/{nombre_parcela}", response_model=list[AlertaResponse])
async def alertas_por_parcela(nombre_parcela: str, db: DB, _: CurrentUser, limit: int = 20):
    return await repo.get_alertas(db, nombre_parcela=nombre_parcela, limit=limit)
