from pydantic import BaseModel, field_validator


class ParcelaCreate(BaseModel):
    nombre_parcela: str

    @field_validator("nombre_parcela")
    @classmethod
    def nombre_no_vacio(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("El nombre de la parcela no puede estar vacío")
        return v.strip()
    coordenadas_parcela: str | None = None
    descripcion_parcela: str | None = None
    nombre_campo: str


class ParcelaUpdate(BaseModel):
    coordenadas_parcela: str | None = None
    descripcion_parcela: str | None = None


class ParcelaResponse(BaseModel):
    nombre_parcela: str
    coordenadas_parcela: str | None = None
    descripcion_parcela: str | None = None
    nombre_campo: str

    model_config = {"from_attributes": True}
