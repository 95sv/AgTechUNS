"""
Dependencias de autenticación / autorización.

`get_current_user`: decodifica el JWT del header Authorization. Devuelve None
si no hay token o es inválido (rutas que pueden ser públicas o protegidas).

`require_admin`: rechaza con 401/403 cualquier request que no traiga un token
válido con el rol "administrador". Lo usan las rutas de gestión.
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError

from src.infrastructure.config import JWT_SECRET, JWT_ALGORITHM

_bearer = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
) -> dict | None:
    if credentials is None:
        return None
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return {"email": payload.get("sub"), "roles": payload.get("roles", [])}
    except JWTError:
        return None


async def require_admin(user: dict | None = Depends(get_current_user)) -> dict:
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No autenticado")
    if "administrador" not in user.get("roles", []):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Requiere rol administrador")
    return user
