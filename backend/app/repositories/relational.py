from datetime import datetime
from sqlalchemy import select, and_, delete as sql_delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.relational import (
    Usuario, Campo, Parcela, Sensor, SensorParcela, Alerta, Prediccion,
    Regla, EjecucionBatch, UsuarioRolCampo, ImagenSatelital, ParcelaImagenSatelital,
)


# ── Usuario ─────────────────────────────────────────────────────────────────

async def get_usuario(db: AsyncSession, email: str) -> Usuario | None:
    result = await db.execute(select(Usuario).where(Usuario.email_usuario == email))
    return result.scalar_one_or_none()


async def create_usuario(db: AsyncSession, email: str, nombre: str, hash_pw: str, telefono: str | None = None) -> Usuario:
    user = Usuario(email_usuario=email, nombre=nombre, hash_password=hash_pw, telefono=telefono)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


# ── Campo ────────────────────────────────────────────────────────────────────

async def get_campos(db: AsyncSession) -> list[Campo]:
    result = await db.execute(select(Campo))
    return list(result.scalars().all())


async def get_campo(db: AsyncSession, nombre: str) -> Campo | None:
    result = await db.execute(select(Campo).where(Campo.nombre_campo == nombre))
    return result.scalar_one_or_none()


async def create_campo(db: AsyncSession, nombre: str, coordenadas: str | None, descripcion: str | None) -> Campo:
    campo = Campo(nombre_campo=nombre, coordenadas_campo=coordenadas, descripcion_campo=descripcion)
    db.add(campo)
    await db.commit()
    await db.refresh(campo)
    return campo


async def update_campo(db: AsyncSession, campo: Campo, coordenadas: str | None, descripcion: str | None) -> Campo:
    if coordenadas is not None:
        campo.coordenadas_campo = coordenadas
    if descripcion is not None:
        campo.descripcion_campo = descripcion
    await db.commit()
    await db.refresh(campo)
    return campo


async def delete_campo(db: AsyncSession, campo: Campo) -> None:
    nombre = campo.nombre_campo
    # 1. Retirar sensores de las parcelas de este campo
    await db.execute(sql_delete(SensorParcela).where(SensorParcela.nombre_campo == nombre))
    # 2. Eliminar parcelas del campo (con sus dependencias directas)
    parcelas = (await db.execute(select(Parcela).where(Parcela.nombre_campo == nombre))).scalars().all()
    for p in parcelas:
        await db.execute(sql_delete(Alerta).where(Alerta.nombre_parcela == p.nombre_parcela))
        await db.execute(sql_delete(Prediccion).where(Prediccion.nombre_parcela == p.nombre_parcela))
        await db.delete(p)
    # 3. Eliminar reglas del campo
    await db.execute(sql_delete(Regla).where(Regla.nombre_campo == nombre))
    # 4. Eliminar el campo
    await db.delete(campo)
    await db.commit()


# ── Parcela ──────────────────────────────────────────────────────────────────

async def get_parcelas(db: AsyncSession, nombre_campo: str | None = None) -> list[Parcela]:
    stmt = select(Parcela)
    if nombre_campo:
        stmt = stmt.where(Parcela.nombre_campo == nombre_campo)
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_parcela(db: AsyncSession, nombre: str) -> Parcela | None:
    result = await db.execute(select(Parcela).where(Parcela.nombre_parcela == nombre))
    return result.scalar_one_or_none()


async def create_parcela(db: AsyncSession, nombre: str, coordenadas: str | None, descripcion: str | None, nombre_campo: str) -> Parcela:
    parcela = Parcela(nombre_parcela=nombre, coordenadas_parcela=coordenadas, descripcion_parcela=descripcion, nombre_campo=nombre_campo)
    db.add(parcela)
    await db.commit()
    await db.refresh(parcela)
    return parcela


async def update_parcela(db: AsyncSession, parcela: Parcela, coordenadas: str | None, descripcion: str | None) -> Parcela:
    if coordenadas is not None:
        parcela.coordenadas_parcela = coordenadas
    if descripcion is not None:
        parcela.descripcion_parcela = descripcion
    await db.commit()
    await db.refresh(parcela)
    return parcela


async def delete_parcela(db: AsyncSession, parcela: Parcela) -> None:
    nombre = parcela.nombre_parcela
    await db.execute(sql_delete(SensorParcela).where(SensorParcela.nombre_parcela == nombre))
    await db.execute(sql_delete(Alerta).where(Alerta.nombre_parcela == nombre))
    await db.execute(sql_delete(Prediccion).where(Prediccion.nombre_parcela == nombre))
    await db.delete(parcela)
    await db.commit()


# ── Sensor ───────────────────────────────────────────────────────────────────

async def get_sensores(db: AsyncSession) -> list[Sensor]:
    result = await db.execute(select(Sensor))
    return list(result.scalars().all())


async def get_sensor(db: AsyncSession, codigo: str) -> Sensor | None:
    result = await db.execute(select(Sensor).where(Sensor.nombre_codigo_sensor == codigo))
    return result.scalar_one_or_none()


async def create_sensor(db: AsyncSession, codigo: str, estado: str = "activo") -> Sensor:
    sensor = Sensor(nombre_codigo_sensor=codigo, estado=estado)
    db.add(sensor)
    await db.commit()
    await db.refresh(sensor)
    return sensor


async def delete_sensor(db: AsyncSession, sensor: Sensor) -> None:
    await db.execute(sql_delete(SensorParcela).where(SensorParcela.nombre_codigo_sensor == sensor.nombre_codigo_sensor))
    await db.delete(sensor)
    await db.commit()


async def get_asignaciones_activas(db: AsyncSession) -> list[SensorParcela]:
    result = await db.execute(
        select(SensorParcela).where(SensorParcela.fecha_retiro == None)  # noqa: E711
    )
    return list(result.scalars().all())


async def desasignar_sensor(db: AsyncSession, codigo_sensor: str, nombre_parcela: str) -> bool:
    result = await db.execute(
        select(SensorParcela)
        .where(SensorParcela.nombre_codigo_sensor == codigo_sensor)
        .where(SensorParcela.nombre_parcela == nombre_parcela)
        .where(SensorParcela.fecha_retiro == None)  # noqa: E711
    )
    sp = result.scalar_one_or_none()
    if not sp:
        return False
    sp.fecha_retiro = datetime.utcnow()
    await db.commit()
    return True


async def get_sensores_parcela(db: AsyncSession, nombre_parcela: str) -> list[SensorParcela]:
    result = await db.execute(
        select(SensorParcela)
        .where(SensorParcela.nombre_parcela == nombre_parcela)
        .where(SensorParcela.fecha_retiro == None)  # noqa: E711
    )
    return list(result.scalars().all())


async def asignar_sensor(
    db: AsyncSession,
    codigo_sensor: str,
    nombre_parcela: str,
    nombre_campo: str,
    fecha_instalacion: datetime,
) -> SensorParcela:
    sp = SensorParcela(
        nombre_codigo_sensor=codigo_sensor,
        nombre_parcela=nombre_parcela,
        nombre_campo=nombre_campo,
        fecha_instalacion=fecha_instalacion,
    )
    db.add(sp)
    await db.commit()
    await db.refresh(sp)
    return sp


# ── Regla ────────────────────────────────────────────────────────────────────

async def get_reglas(db: AsyncSession, nombre_campo: str | None = None) -> list[Regla]:
    stmt = select(Regla)
    if nombre_campo:
        stmt = stmt.where(Regla.nombre_campo == nombre_campo)
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_regla(db: AsyncSession, nombre: str) -> Regla | None:
    result = await db.execute(select(Regla).where(Regla.nombre_regla == nombre))
    return result.scalar_one_or_none()


async def create_regla(db: AsyncSession, nombre: str, formula: str, descripcion: str | None, umbral: float, nombre_campo: str) -> Regla:
    regla = Regla(nombre_regla=nombre, formula=formula, descripcion_regla=descripcion, umbral=umbral, nombre_campo=nombre_campo)
    db.add(regla)
    await db.commit()
    await db.refresh(regla)
    return regla


async def update_regla(db: AsyncSession, regla: Regla, formula: str | None, descripcion: str | None, umbral: float | None) -> Regla:
    if formula is not None:
        regla.formula = formula
    if descripcion is not None:
        regla.descripcion_regla = descripcion
    if umbral is not None:
        regla.umbral = umbral
    await db.commit()
    await db.refresh(regla)
    return regla


async def delete_regla(db: AsyncSession, regla: Regla) -> None:
    await db.delete(regla)
    await db.commit()


# ── Alerta ───────────────────────────────────────────────────────────────────

async def get_alertas(db: AsyncSession, nombre_parcela: str | None = None, limit: int = 50) -> list[Alerta]:
    stmt = select(Alerta).order_by(Alerta.fecha_emision.desc()).limit(limit)
    if nombre_parcela:
        stmt = stmt.where(Alerta.nombre_parcela == nombre_parcela)
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def create_alerta(db: AsyncSession, mensaje: str, nombre_parcela: str, email_usuario: str) -> Alerta:
    alerta = Alerta(
        mensaje=mensaje,
        nombre_parcela=nombre_parcela,
        email_usuario=email_usuario,
        fecha_emision=datetime.utcnow(),
    )
    db.add(alerta)
    await db.commit()
    await db.refresh(alerta)
    return alerta


# ── Predicción ───────────────────────────────────────────────────────────────

async def get_predicciones(db: AsyncSession, nombre_parcela: str | None = None, limit: int = 20) -> list[Prediccion]:
    stmt = select(Prediccion).order_by(Prediccion.fecha_emision.desc()).limit(limit)
    if nombre_parcela:
        stmt = stmt.where(Prediccion.nombre_parcela == nombre_parcela)
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def create_prediccion(
    db: AsyncSession,
    resultado: str,
    fecha_ini: datetime,
    fecha_fin: datetime,
    nombre_parcela: str,
    fecha_batch: datetime | None = None,
) -> Prediccion:
    p = Prediccion(
        resultado=resultado,
        fecha_ini=fecha_ini,
        fecha_fin=fecha_fin,
        nombre_parcela=nombre_parcela,
        fecha_batch=fecha_batch,
        fecha_emision=datetime.utcnow(),
    )
    db.add(p)
    await db.commit()
    await db.refresh(p)
    return p


# ── EjecucionBatch ────────────────────────────────────────────────────────────

async def create_ejecucion_batch(db: AsyncSession, fecha_ini: datetime) -> EjecucionBatch:
    eb = EjecucionBatch(fecha_ini=fecha_ini, estado="en_progreso")
    db.add(eb)
    await db.commit()
    await db.refresh(eb)
    return eb


async def finish_ejecucion_batch(db: AsyncSession, eb: EjecucionBatch, estado: str = "completado") -> EjecucionBatch:
    eb.estado = estado
    eb.fecha_fin = datetime.utcnow()
    await db.commit()
    await db.refresh(eb)
    return eb


async def get_ejecucion_batch(db: AsyncSession, fecha_ini: datetime) -> EjecucionBatch | None:
    result = await db.execute(
        select(EjecucionBatch).where(EjecucionBatch.fecha_ini == fecha_ini)
    )
    return result.scalar_one_or_none()


# ── Imagen Satelital ──────────────────────────────────────────────────────────

async def create_imagen_satelital(db: AsyncSession, fecha_captura: datetime, proveedor: str) -> ImagenSatelital:
    img = ImagenSatelital(fecha_captura=fecha_captura, proveedor=proveedor)
    db.add(img)
    await db.commit()
    await db.refresh(img)
    return img


async def asignar_imagen_parcela(
    db: AsyncSession,
    id_imagen: int,
    nombre_parcela: str,
    ndvi: float | None,
    ndmi: float | None,
) -> ParcelaImagenSatelital:
    pis = ParcelaImagenSatelital(
        id_imagen=id_imagen,
        nombre_parcela=nombre_parcela,
        indice_ndvi=ndvi,
        indice_ndmi=ndmi,
    )
    db.add(pis)
    await db.commit()
    await db.refresh(pis)
    return pis


async def get_ultima_imagen_parcela(db: AsyncSession, nombre_parcela: str) -> ParcelaImagenSatelital | None:
    result = await db.execute(
        select(ParcelaImagenSatelital)
        .join(ImagenSatelital)
        .where(ParcelaImagenSatelital.nombre_parcela == nombre_parcela)
        .order_by(ImagenSatelital.fecha_captura.desc())
        .limit(1)
    )
    return result.scalar_one_or_none()


# ── Usuarios de un campo ──────────────────────────────────────────────────────

async def asignar_usuario_campo(
    db: AsyncSession, email: str, nombre_rol: str, nombre_campo: str
) -> UsuarioRolCampo:
    urc = UsuarioRolCampo(email_usuario=email, nombre_rol=nombre_rol, nombre_campo=nombre_campo)
    db.add(urc)
    await db.commit()
    await db.refresh(urc)
    return urc


async def get_campos_usuario(db: AsyncSession, email: str) -> list[str]:
    result = await db.execute(
        select(UsuarioRolCampo.nombre_campo).where(UsuarioRolCampo.email_usuario == email)
    )
    return [row[0] for row in result.all()]
