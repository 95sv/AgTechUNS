from datetime import datetime
from sqlalchemy import String, Float, DateTime, ForeignKey, Text, Boolean, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class Usuario(Base):
    __tablename__ = "usuario"

    email_usuario: Mapped[str] = mapped_column(String, primary_key=True)
    nombre: Mapped[str] = mapped_column(String(255))
    telefono: Mapped[str | None] = mapped_column(String(50))
    hash_password: Mapped[str] = mapped_column(String)

    roles_campos: Mapped[list["UsuarioRolCampo"]] = relationship(back_populates="usuario")
    alertas: Mapped[list["Alerta"]] = relationship(back_populates="usuario")


class Campo(Base):
    __tablename__ = "campo"

    nombre_campo: Mapped[str] = mapped_column(String(255), primary_key=True)
    coordenadas_campo: Mapped[str | None] = mapped_column(Text)
    descripcion_campo: Mapped[str | None] = mapped_column(Text)

    parcelas: Mapped[list["Parcela"]] = relationship(back_populates="campo")
    reglas: Mapped[list["Regla"]] = relationship(back_populates="campo")
    roles_usuarios: Mapped[list["UsuarioRolCampo"]] = relationship(back_populates="campo")


class Rol(Base):
    __tablename__ = "rol"

    nombre_rol: Mapped[str] = mapped_column(String(100), primary_key=True)
    descripcion: Mapped[str | None] = mapped_column(Text)

    usuarios_campos: Mapped[list["UsuarioRolCampo"]] = relationship(back_populates="rol")


class Cultivo(Base):
    __tablename__ = "cultivo"

    nombre_cultivo: Mapped[str] = mapped_column(String(255), primary_key=True)
    variedad: Mapped[str | None] = mapped_column(String(255))

    registros: Mapped[list["RegistroCultivo"]] = relationship(back_populates="cultivo")


class Sensor(Base):
    __tablename__ = "sensor"

    nombre_codigo_sensor: Mapped[str] = mapped_column(String(100), primary_key=True)
    estado: Mapped[str] = mapped_column(String(50), default="activo")

    parcelas: Mapped[list["SensorParcela"]] = relationship(back_populates="sensor")


class ImagenSatelital(Base):
    __tablename__ = "imagen_satelital"

    id_imagen: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    fecha_captura: Mapped[datetime] = mapped_column(DateTime)
    proveedor: Mapped[str] = mapped_column(String(100))

    parcelas: Mapped[list["ParcelaImagenSatelital"]] = relationship(back_populates="imagen")


class EjecucionBatch(Base):
    __tablename__ = "ejecucion_batch"

    fecha_ini: Mapped[datetime] = mapped_column(DateTime, primary_key=True)
    estado: Mapped[str] = mapped_column(String(50))
    fecha_fin: Mapped[datetime | None] = mapped_column(DateTime)

    predicciones: Mapped[list["Prediccion"]] = relationship(back_populates="ejecucion_batch")


class Parcela(Base):
    __tablename__ = "parcela"

    nombre_parcela: Mapped[str] = mapped_column(String(255), primary_key=True)
    coordenadas_parcela: Mapped[str | None] = mapped_column(Text)
    descripcion_parcela: Mapped[str | None] = mapped_column(Text)
    nombre_campo: Mapped[str] = mapped_column(String(255), ForeignKey("campo.nombre_campo"))

    campo: Mapped["Campo"] = relationship(back_populates="parcelas")
    ventanas_temporales: Mapped[list["VentanaTemporal"]] = relationship(back_populates="parcela")
    alertas: Mapped[list["Alerta"]] = relationship(back_populates="parcela")
    predicciones: Mapped[list["Prediccion"]] = relationship(back_populates="parcela")
    imagenes: Mapped[list["ParcelaImagenSatelital"]] = relationship(back_populates="parcela")
    sensores: Mapped[list["SensorParcela"]] = relationship(back_populates="parcela")
    registros_cultivo: Mapped[list["RegistroCultivo"]] = relationship(back_populates="parcela")


class Regla(Base):
    __tablename__ = "regla"

    nombre_regla: Mapped[str] = mapped_column(String(255), primary_key=True)
    formula: Mapped[str] = mapped_column(Text)
    descripcion_regla: Mapped[str | None] = mapped_column(Text)
    umbral: Mapped[float] = mapped_column(Float)
    nombre_campo: Mapped[str] = mapped_column(String(255), ForeignKey("campo.nombre_campo"))

    campo: Mapped["Campo"] = relationship(back_populates="reglas")


class VentanaTemporal(Base):
    __tablename__ = "ventana_temporal"

    fecha_ini: Mapped[datetime] = mapped_column(DateTime, primary_key=True)
    fecha_fin: Mapped[datetime] = mapped_column(DateTime, primary_key=True)
    nombre_parcela: Mapped[str] = mapped_column(
        String(255), ForeignKey("parcela.nombre_parcela"), primary_key=True
    )

    parcela: Mapped["Parcela"] = relationship(back_populates="ventanas_temporales")


class Alerta(Base):
    __tablename__ = "alerta"

    id_alerta: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    fecha_emision: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    mensaje: Mapped[str] = mapped_column(Text)
    nombre_parcela: Mapped[str] = mapped_column(String(255), ForeignKey("parcela.nombre_parcela"))
    email_usuario: Mapped[str] = mapped_column(String(255), ForeignKey("usuario.email_usuario"))

    parcela: Mapped["Parcela"] = relationship(back_populates="alertas")
    usuario: Mapped["Usuario"] = relationship(back_populates="alertas")


class Prediccion(Base):
    __tablename__ = "prediccion"

    id_prediccion: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    fecha_emision: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    resultado: Mapped[str] = mapped_column(Text)
    fecha_ini: Mapped[datetime] = mapped_column(DateTime)
    fecha_fin: Mapped[datetime] = mapped_column(DateTime)
    nombre_parcela: Mapped[str] = mapped_column(String(255), ForeignKey("parcela.nombre_parcela"))
    fecha_batch: Mapped[datetime | None] = mapped_column(
        DateTime, ForeignKey("ejecucion_batch.fecha_ini")
    )

    parcela: Mapped["Parcela"] = relationship(back_populates="predicciones")
    ejecucion_batch: Mapped["EjecucionBatch | None"] = relationship(back_populates="predicciones")


# ── Tablas asociativas ──────────────────────────────────────────────────────

class UsuarioRolCampo(Base):
    __tablename__ = "usuario_rol_campo"

    email_usuario: Mapped[str] = mapped_column(
        String(255), ForeignKey("usuario.email_usuario"), primary_key=True
    )
    nombre_rol: Mapped[str] = mapped_column(
        String(100), ForeignKey("rol.nombre_rol"), primary_key=True
    )
    nombre_campo: Mapped[str] = mapped_column(
        String(255), ForeignKey("campo.nombre_campo"), primary_key=True
    )

    usuario: Mapped["Usuario"] = relationship(back_populates="roles_campos")
    rol: Mapped["Rol"] = relationship(back_populates="usuarios_campos")
    campo: Mapped["Campo"] = relationship(back_populates="roles_usuarios")


class ParcelaImagenSatelital(Base):
    __tablename__ = "parcela_imagen_satelital"

    id_imagen: Mapped[int] = mapped_column(
        Integer, ForeignKey("imagen_satelital.id_imagen"), primary_key=True
    )
    nombre_parcela: Mapped[str] = mapped_column(
        String(255), ForeignKey("parcela.nombre_parcela"), primary_key=True
    )
    indice_ndvi: Mapped[float | None] = mapped_column(Float)
    indice_ndmi: Mapped[float | None] = mapped_column(Float)

    imagen: Mapped["ImagenSatelital"] = relationship(back_populates="parcelas")
    parcela: Mapped["Parcela"] = relationship(back_populates="imagenes")


class RegistroCultivo(Base):
    __tablename__ = "registro_cultivo"

    nombre_parcela: Mapped[str] = mapped_column(
        String(255), ForeignKey("parcela.nombre_parcela"), primary_key=True
    )
    nombre_cultivo: Mapped[str] = mapped_column(
        String(255), ForeignKey("cultivo.nombre_cultivo"), primary_key=True
    )
    fecha_siembra: Mapped[datetime] = mapped_column(DateTime, primary_key=True)
    fecha_cosecha: Mapped[datetime | None] = mapped_column(DateTime)

    parcela: Mapped["Parcela"] = relationship(back_populates="registros_cultivo")
    cultivo: Mapped["Cultivo"] = relationship(back_populates="registros")


class SensorParcela(Base):
    __tablename__ = "sensor_parcela"

    nombre_codigo_sensor: Mapped[str] = mapped_column(
        String(100), ForeignKey("sensor.nombre_codigo_sensor"), primary_key=True
    )
    nombre_parcela: Mapped[str] = mapped_column(
        String(255), ForeignKey("parcela.nombre_parcela"), primary_key=True
    )
    nombre_campo: Mapped[str] = mapped_column(
        String(255), ForeignKey("campo.nombre_campo"), primary_key=True
    )
    fecha_instalacion: Mapped[datetime] = mapped_column(DateTime, primary_key=True)
    fecha_retiro: Mapped[datetime | None] = mapped_column(DateTime)

    sensor: Mapped["Sensor"] = relationship(back_populates="parcelas")
    parcela: Mapped["Parcela"] = relationship(back_populates="sensores")
