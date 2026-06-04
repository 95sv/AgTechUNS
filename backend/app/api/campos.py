from fastapi import APIRouter, HTTPException
from app.api.deps import DB, CurrentUser
from app.repositories import relational as repo
from app.schemas.campo import CampoCreate, CampoUpdate, CampoResponse, AsignarUsuarioRequest

router = APIRouter()


@router.get("/", response_model=list[CampoResponse])
async def listar_campos(db: DB, _: CurrentUser):
    return await repo.get_campos(db)


@router.post("/", response_model=CampoResponse, status_code=201)
async def crear_campo(body: CampoCreate, db: DB, _: CurrentUser):
    if await repo.get_campo(db, body.nombre_campo):
        raise HTTPException(400, "Ya existe un campo con ese nombre")
    return await repo.create_campo(db, body.nombre_campo, body.coordenadas_campo, body.descripcion_campo)


@router.get("/{nombre_campo}", response_model=CampoResponse)
async def obtener_campo(nombre_campo: str, db: DB, _: CurrentUser):
    campo = await repo.get_campo(db, nombre_campo)
    if not campo:
        raise HTTPException(404, "Campo no encontrado")
    return campo


@router.put("/{nombre_campo}", response_model=CampoResponse)
async def actualizar_campo(nombre_campo: str, body: CampoUpdate, db: DB, _: CurrentUser):
    campo = await repo.get_campo(db, nombre_campo)
    if not campo:
        raise HTTPException(404, "Campo no encontrado")
    return await repo.update_campo(db, campo, body.coordenadas_campo, body.descripcion_campo)


@router.post("/{nombre_campo}/eliminar")
async def eliminar_campo(nombre_campo: str, db: DB, _: CurrentUser):
    campo = await repo.get_campo(db, nombre_campo)
    if not campo:
        raise HTTPException(404, "Campo no encontrado")
    await repo.delete_campo(db, campo)
    return {"ok": True}


@router.post("/{nombre_campo}/usuarios", status_code=201)
async def asignar_usuario(nombre_campo: str, body: AsignarUsuarioRequest, db: DB, _: CurrentUser):
    campo = await repo.get_campo(db, nombre_campo)
    if not campo:
        raise HTTPException(404, "Campo no encontrado")
    usuario = await repo.get_usuario(db, body.email_usuario)
    if not usuario:
        raise HTTPException(404, "Usuario no encontrado")
    await repo.asignar_usuario_campo(db, body.email_usuario, body.nombre_rol, nombre_campo)
    return {"message": f"Usuario {body.email_usuario} asignado al campo {nombre_campo} como {body.nombre_rol}"}


@router.get("/{nombre_campo}/parcelas")
async def parcelas_del_campo(nombre_campo: str, db: DB, _: CurrentUser):
    from app.schemas.parcela import ParcelaResponse
    parcelas = await repo.get_parcelas(db, nombre_campo=nombre_campo)
    return parcelas


@router.get("/{nombre_campo}/reglas")
async def reglas_del_campo(nombre_campo: str, db: DB, _: CurrentUser):
    from app.schemas.regla import ReglaResponse
    return await repo.get_reglas(db, nombre_campo=nombre_campo)
