from fastapi import APIRouter, HTTPException
from app.api.deps import DB, CurrentUser
from app.repositories import relational as repo
from app.repositories.timeseries import TimeSeriesRepository
from app.schemas.sensor import SensorCreate, SensorResponse, AsignarSensorRequest, LecturaSensor

router = APIRouter()
ts_repo = TimeSeriesRepository()


@router.get("/", response_model=list[SensorResponse])
async def listar_sensores(db: DB, _: CurrentUser):
    return await repo.get_sensores(db)


@router.get("/asignaciones")
async def listar_asignaciones(db: DB, _: CurrentUser):
    asignaciones = await repo.get_asignaciones_activas(db)
    return [
        {
            "nombre_codigo_sensor": a.nombre_codigo_sensor,
            "nombre_parcela": a.nombre_parcela,
            "nombre_campo": a.nombre_campo,
            "fecha_instalacion": a.fecha_instalacion,
        }
        for a in asignaciones
    ]


@router.post("/", response_model=SensorResponse, status_code=201)
async def crear_sensor(body: SensorCreate, db: DB, _: CurrentUser):
    if await repo.get_sensor(db, body.nombre_codigo_sensor):
        raise HTTPException(400, "Ya existe un sensor con ese código")
    return await repo.create_sensor(db, body.nombre_codigo_sensor, body.estado)


@router.post("/{codigo_sensor}/eliminar")
async def eliminar_sensor(codigo_sensor: str, db: DB, _: CurrentUser):
    sensor = await repo.get_sensor(db, codigo_sensor)
    if not sensor:
        raise HTTPException(404, "Sensor no encontrado")
    await repo.delete_sensor(db, sensor)
    return {"ok": True}


@router.post("/{codigo_sensor}/parcela/{nombre_parcela}/retirar")
async def desasignar_sensor(codigo_sensor: str, nombre_parcela: str, db: DB, _: CurrentUser):
    eliminado = await repo.desasignar_sensor(db, codigo_sensor, nombre_parcela)
    if not eliminado:
        raise HTTPException(404, "Asignación activa no encontrada")
    return {"ok": True}


@router.get("/{codigo_sensor}", response_model=SensorResponse)
async def obtener_sensor(codigo_sensor: str, db: DB, _: CurrentUser):
    sensor = await repo.get_sensor(db, codigo_sensor)
    if not sensor:
        raise HTTPException(404, "Sensor no encontrado")
    return sensor


@router.post("/{codigo_sensor}/asignar", status_code=201)
async def asignar_sensor_a_parcela(codigo_sensor: str, body: AsignarSensorRequest, db: DB, _: CurrentUser):
    sensor = await repo.get_sensor(db, codigo_sensor)
    if not sensor:
        raise HTTPException(404, "Sensor no encontrado")
    parcela = await repo.get_parcela(db, body.nombre_parcela)
    if not parcela:
        raise HTTPException(404, "Parcela no encontrada")
    fecha = body.fecha_instalacion.replace(tzinfo=None)
    sp = await repo.asignar_sensor(
        db,
        codigo_sensor,
        body.nombre_parcela,
        body.nombre_campo,
        fecha,
    )
    return {"message": "Sensor asignado", "sensor": codigo_sensor, "parcela": body.nombre_parcela}


@router.get("/{codigo_sensor}/lecturas", response_model=list[LecturaSensor])
async def lecturas_sensor(codigo_sensor: str, horas: int = 24, _: CurrentUser = None):
    lecturas = await ts_repo.get_lecturas_parcela([codigo_sensor], horas=horas)
    return [
        LecturaSensor(
            sensor=l["sensor"],
            timestamp=l["timestamp"],
            temperatura=l.get("temperatura"),
            humedad=l.get("humedad"),
            ph=l.get("ph"),
        )
        for l in lecturas
    ]


@router.get("/{codigo_sensor}/ultima-lectura")
async def ultima_lectura(codigo_sensor: str, _: CurrentUser = None):
    lectura = await ts_repo.get_ultima_lectura(codigo_sensor)
    if not lectura:
        raise HTTPException(404, "Sin lecturas recientes para este sensor")
    return lectura
