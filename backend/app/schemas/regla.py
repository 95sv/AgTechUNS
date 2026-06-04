from pydantic import BaseModel


class ReglaCreate(BaseModel):
    nombre_regla: str
    formula: str
    descripcion_regla: str | None = None
    umbral: float
    nombre_campo: str


class ReglaUpdate(BaseModel):
    formula: str | None = None
    descripcion_regla: str | None = None
    umbral: float | None = None


class ReglaResponse(BaseModel):
    nombre_regla: str
    formula: str
    descripcion_regla: str | None = None
    umbral: float
    nombre_campo: str

    model_config = {"from_attributes": True}
