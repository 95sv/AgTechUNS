"""
Adapter secundario: lee las parcelas desde un archivo JSON.

El archivo se monta como volumen en docker-compose, así que cualquier cambio
queda visible para el contenedor con sólo reiniciarlo (no requiere rebuild).

Implementa ParcelaRepositoryPort. Cuando se implemente el repositorio
relacional, se creará un PostgresParcelaRepository que implemente el mismo
Port y los routers no se enteran.
"""
from __future__ import annotations
import json
import logging
import os
from pathlib import Path

from src.domain.entities.parcela import Parcela

_log = logging.getLogger("json_parcela_repository")

DEFAULT_PATH = "/app/config/parcelas.json"

# Fallback si el archivo no existe (defensa para desarrollo local).
PARCELAS_FALLBACK = [
    Parcela(nombre_parcela="Parcela-Norte", nombre_codigo_sensor="SN-001", lat=-38.71, lon=-62.27),
    Parcela(nombre_parcela="Parcela-Sur",   nombre_codigo_sensor="SN-002", lat=-38.75, lon=-62.30),
]


class JsonParcelaRepository:
    def __init__(self, path: str | None = None):
        self._path = Path(path or os.getenv("PARCELAS_CONFIG_PATH", DEFAULT_PATH))

    async def listar(self) -> list[Parcela]:
        if not self._path.exists():
            _log.warning("Archivo de parcelas no encontrado en %s; usando fallback", self._path)
            return list(PARCELAS_FALLBACK)
        try:
            with self._path.open(encoding="utf-8") as f:
                data = json.load(f)
            return [Parcela(**p) for p in data["parcelas"]]
        except Exception as exc:  # noqa: BLE001
            _log.error("Error leyendo %s: %s. Usando fallback.", self._path, exc)
            return list(PARCELAS_FALLBACK)
