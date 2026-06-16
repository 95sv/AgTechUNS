"""
Puerto secundario: contrato para acceder a las parcelas configuradas.
Lo implementa cualquier adapter (JSON hoy, PostgreSQL mañana).
"""
from typing import Protocol

from src.domain.entities.parcela import Parcela


class ParcelaRepositoryPort(Protocol):
    async def listar(self) -> list[Parcela]: ...
