"""
Entidades de usuario y credenciales — utilizadas por el caso de uso de
autenticación. Heredadas del modelo del Sign In Controller original.
"""
from __future__ import annotations
from pydantic import BaseModel, EmailStr


class Credenciales(BaseModel):
    email: EmailStr
    password: str


class Usuario(BaseModel):
    email: EmailStr
    nombre: str
    roles: list[str]


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
