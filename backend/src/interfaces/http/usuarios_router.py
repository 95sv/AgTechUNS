"""
Router de gestión de Usuarios — CU-10 / CU-11.

Permite registrar usuarios con rol (ADMIN, AGRONOMO, PRODUCTOR).
MVP: usuarios hardcodeados en MockUserRepository; este endpoint es el punto
de entrada definido en el contrato de API (YAML Entrega 4).
"""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr

from src.interfaces.http.auth_dependency import require_admin

router = APIRouter(prefix="/usuarios", tags=["Catálogos y Configuración"])

ROL_VALIDOS = {"ADMIN", "AGRONOMO", "PRODUCTOR"}


class NuevoUsuario(BaseModel):
    email: EmailStr
    rol: str


@router.post("", status_code=status.HTTP_201_CREATED)
async def registrar_usuario(
    usuario: NuevoUsuario,
    _: dict = Depends(require_admin),
) -> dict:
    if usuario.rol not in ROL_VALIDOS:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Rol inválido. Válidos: {ROL_VALIDOS}",
        )
    return {
        "mensaje": f"Usuario {usuario.email} con rol {usuario.rol} registrado (persistencia relacional pendiente).",
        "email": usuario.email,
        "rol": usuario.rol,
    }
