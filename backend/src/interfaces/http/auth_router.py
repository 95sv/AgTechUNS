from fastapi import APIRouter, Depends, HTTPException, Request, status
from slowapi import Limiter
from slowapi.util import get_remote_address

from src.application.authenticate_user import AuthenticateUser, CredencialesInvalidas
from src.domain.entities.usuario import Credenciales, Token
from src.interfaces.http.auth_dependency import get_current_user
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


@router.get("/me")
async def me(user: dict | None = Depends(get_current_user)) -> dict:
    """Devuelve los datos del usuario actual (o {"anonimo": True} si no hay sesión)."""
    return user or {"anonimo": True}
