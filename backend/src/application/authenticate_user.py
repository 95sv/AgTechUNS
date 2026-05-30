"""
Caso de uso: Autenticar un usuario y emitir un token JWT.

Mantiene la lógica original del Sign In Controller pero ahora desacoplada
del framework HTTP: este servicio no sabe que existe FastAPI.
"""
from __future__ import annotations
import os
from datetime import datetime, timedelta, timezone

from jose import jwt

from src.domain.entities.usuario import Credenciales, Token
from src.domain.ports.user_repository_port import UserRepositoryPort

JWT_SECRET = os.getenv("JWT_SECRET", "agtech-dev-secret-cambiar-en-prod")
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_MINUTES = 60


class CredencialesInvalidas(Exception):
    pass


class AuthenticateUser:
    def __init__(self, user_repo: UserRepositoryPort):
        self._users = user_repo

    async def execute(self, credenciales: Credenciales) -> Token:
        ok = await self._users.verificar_password(credenciales.email, credenciales.password)
        if not ok:
            raise CredencialesInvalidas("Email o contraseña inválidos")
        usuario = await self._users.buscar_por_email(credenciales.email)
        if usuario is None:
            raise CredencialesInvalidas("Usuario no encontrado")
        payload = {
            "sub": usuario.email,
            "roles": usuario.roles,
            "exp": datetime.now(timezone.utc) + timedelta(minutes=JWT_EXPIRE_MINUTES),
        }
        access_token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
        return Token(access_token=access_token)
