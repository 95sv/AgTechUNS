from pydantic import BaseModel, field_validator


class CampoCreate(BaseModel):
    nombre_campo: str

    @field_validator("nombre_campo")
    @classmethod
    def nombre_no_vacio(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("El nombre del campo no puede estar vacío")
        return v.strip()
    coordenadas_campo: str | None = None
    descripcion_campo: str | None = None


class CampoUpdate(BaseModel):
    coordenadas_campo: str | None = None
    descripcion_campo: str | None = None


class CampoResponse(BaseModel):
    nombre_campo: str
    coordenadas_campo: str | None = None
    descripcion_campo: str | None = None

    model_config = {"from_attributes": True}


class AsignarUsuarioRequest(BaseModel):
    email_usuario: str
    nombre_rol: str
