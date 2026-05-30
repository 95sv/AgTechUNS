"""
Puerto secundario para el repositorio de usuarios.
"""
from __future__ import annotations
from typing import Protocol

from src.domain.entities.usuario import Usuario


class UserRepositoryPort(Protocol):
    async def buscar_por_email(self, email: str) -> Usuario | None: ...
    async def verificar_password(self, email: str, password: str) -> bool: ...
