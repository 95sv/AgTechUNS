"""
Adapter secundario: implementación mock del puerto UserRepositoryPort.

Se mantiene mientras no esté implementado el repositorio relacional sobre
PostgreSQL. Heredado del Sign In Controller original.
"""
from __future__ import annotations
from src.domain.entities.usuario import Usuario

_MOCK_USERS = {
    "admin@agtech.com": {
        "password": "admin123",
        "usuario": Usuario(email="admin@agtech.com", nombre="Administrador", roles=["administrador"]),
    },
    "agronomo@agtech.com": {
        "password": "agronomo123",
        "usuario": Usuario(email="agronomo@agtech.com", nombre="Agrónomo", roles=["agronomo"]),
    },
    "agricultor@agtech.com": {
        "password": "agricultor123",
        "usuario": Usuario(email="agricultor@agtech.com", nombre="Agricultor", roles=["agricultor"]),
    },
}


class MockUserRepository:
    async def buscar_por_email(self, email: str) -> Usuario | None:
        rec = _MOCK_USERS.get(email)
        return rec["usuario"] if rec else None

    async def verificar_password(self, email: str, password: str) -> bool:
        rec = _MOCK_USERS.get(email)
        return rec is not None and rec["password"] == password
