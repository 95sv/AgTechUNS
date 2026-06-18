"""
Entidades de usuario y credenciales — utilizadas por el caso de uso de
autenticación. Heredadas del modelo del Sign In Controller original.
"""
from __future__ import annotations
from pydantic import BaseModel, EmailStr, Field, ConfigDict


class Credenciales(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    email_usuario: EmailStr = Field(alias="emailUsuario")
    password: str


class Usuario(BaseModel):
    email: EmailStr
    nombre: str
    roles: list[str]


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
