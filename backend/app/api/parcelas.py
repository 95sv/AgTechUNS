from fastapi import APIRouter, HTTPException
from app.api.deps import DB, CurrentUser
from app.repositories import relational as repo
from app.schemas.parcela import ParcelaCreate, ParcelaUpdate, ParcelaResponse

router = APIRouter()


@router.get("/", response_model=list[ParcelaResponse])
async def listar_parcelas(db: DB, _: CurrentUser, nombre_campo: str | None = None):
    return await repo.get_parcelas(db, nombre_campo=nombre_campo)


@router.post("/", response_model=ParcelaResponse, status_code=201)
async def crear_parcela(body: ParcelaCreate, db: DB, _: CurrentUser):
    if await repo.get_parcela(db, body.nombre_parcela):
        raise HTTPException(400, "Ya existe una parcela con ese nombre")
    campo = await repo.get_campo(db, body.nombre_campo)
    if not campo:
        raise HTTPException(404, "Campo no encontrado")
    return await repo.create_parcela(db, body.nombre_parcela, body.coordenadas_parcela, body.descripcion_parcela, body.nombre_campo)


@router.get("/{nombre_parcela}", response_model=ParcelaResponse)
async def obtener_parcela(nombre_parcela: str, db: DB, _: CurrentUser):
    parcela = await repo.get_parcela(db, nombre_parcela)
    if not parcela:
        raise HTTPException(404, "Parcela no encontrada")
    return parcela


@router.put("/{nombre_parcela}", response_model=ParcelaResponse)
async def actualizar_parcela(nombre_parcela: str, body: ParcelaUpdate, db: DB, _: CurrentUser):
    parcela = await repo.get_parcela(db, nombre_parcela)
    if not parcela:
        raise HTTPException(404, "Parcela no encontrada")
    return await repo.update_parcela(db, parcela, body.coordenadas_parcela, body.descripcion_parcela)


@router.post("/{nombre_parcela}/eliminar")
async def eliminar_parcela(nombre_parcela: str, db: DB, _: CurrentUser):
    parcela = await repo.get_parcela(db, nombre_parcela)
    if not parcela:
        raise HTTPException(404, "Parcela no encontrada")
    await repo.delete_parcela(db, parcela)
    return {"ok": True}


@router.get("/{nombre_parcela}/sensores")
async def sensores_de_parcela(nombre_parcela: str, db: DB, _: CurrentUser):
    parcela = await repo.get_parcela(db, nombre_parcela)
    if not parcela:
        raise HTTPException(404, "Parcela no encontrada")
    return await repo.get_sensores_parcela(db, nombre_parcela)


@router.get("/{nombre_parcela}/alertas")
async def alertas_parcela(nombre_parcela: str, db: DB, _: CurrentUser):
    return await repo.get_alertas(db, nombre_parcela=nombre_parcela)


@router.get("/{nombre_parcela}/predicciones")
async def predicciones_parcela(nombre_parcela: str, db: DB, _: CurrentUser):
    return await repo.get_predicciones(db, nombre_parcela=nombre_parcela)
