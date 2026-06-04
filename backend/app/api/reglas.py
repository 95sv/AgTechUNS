from fastapi import APIRouter, HTTPException
from app.api.deps import DB, CurrentUser
from app.repositories import relational as repo
from app.schemas.regla import ReglaCreate, ReglaUpdate, ReglaResponse

router = APIRouter()


@router.get("/", response_model=list[ReglaResponse])
async def listar_reglas(db: DB, _: CurrentUser, nombre_campo: str | None = None):
    return await repo.get_reglas(db, nombre_campo=nombre_campo)


@router.post("/", response_model=ReglaResponse, status_code=201)
async def crear_regla(body: ReglaCreate, db: DB, _: CurrentUser):
    if await repo.get_regla(db, body.nombre_regla):
        raise HTTPException(400, "Ya existe una regla con ese nombre")
    campo = await repo.get_campo(db, body.nombre_campo)
    if not campo:
        raise HTTPException(404, "Campo no encontrado")
    return await repo.create_regla(db, body.nombre_regla, body.formula, body.descripcion_regla, body.umbral, body.nombre_campo)


@router.get("/{nombre_regla}", response_model=ReglaResponse)
async def obtener_regla(nombre_regla: str, db: DB, _: CurrentUser):
    regla = await repo.get_regla(db, nombre_regla)
    if not regla:
        raise HTTPException(404, "Regla no encontrada")
    return regla


@router.put("/{nombre_regla}", response_model=ReglaResponse)
async def actualizar_regla(nombre_regla: str, body: ReglaUpdate, db: DB, _: CurrentUser):
    regla = await repo.get_regla(db, nombre_regla)
    if not regla:
        raise HTTPException(404, "Regla no encontrada")
    return await repo.update_regla(db, regla, body.formula, body.descripcion_regla, body.umbral)


@router.post("/{nombre_regla}/eliminar")
async def eliminar_regla(nombre_regla: str, db: DB, _: CurrentUser):
    regla = await repo.get_regla(db, nombre_regla)
    if not regla:
        raise HTTPException(404, "Regla no encontrada")
    await repo.delete_regla(db, regla)
    return {"ok": True}
