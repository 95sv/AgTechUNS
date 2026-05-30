"""
Router HTTP de autenticación. Adapter primario que traduce HTTP a invocaciones
del caso de uso AuthenticateUser.
"""
from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException, Request, status
from slowapi import Limiter
from slowapi.util import get_remote_address

from src.application.authenticate_user import AuthenticateUser, CredencialesInvalidas
from src.domain.entities.usuario import Credenciales, Token
from src.interfaces.http.dependencies import get_authenticate_use_case

router = APIRouter(prefix="/auth", tags=["Autenticación"])
limiter = Limiter(key_func=get_remote_address)


@router.post("/login", response_model=Token)
@limiter.limit("5/minute")
async def login(
    request: Request,
    credenciales: Credenciales,
    use_case: AuthenticateUser = Depends(get_authenticate_use_case),
) -> Token:
    try:
        return await use_case.execute(credenciales)
    except CredencialesInvalidas:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña inválidos",
        )
