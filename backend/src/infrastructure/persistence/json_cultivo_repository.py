import os
from pathlib import Path

from src.domain.entities.cultivo import Cultivo
from src.infrastructure.persistence._json_store import leer_json, escribir_json

DEFAULT_PATH = "/app/config/cultivos.json"


class CultivoYaExiste(Exception): pass
class CultivoNoEncontrado(Exception): pass


class JsonCultivoRepository:
    def __init__(self, path: str | None = None):
        self._path = Path(path or os.getenv("CULTIVOS_CONFIG_PATH", DEFAULT_PATH))

    def _load(self) -> list[Cultivo]:
        data = leer_json(self._path)
        return [Cultivo(**c) for c in data.get("cultivos", [])]

    def _save(self, cultivos: list[Cultivo]) -> None:
        escribir_json(self._path, {"cultivos": [c.model_dump() for c in cultivos]})

    async def listar(self) -> list[Cultivo]:
        return self._load()

    async def crear(self, cultivo: Cultivo) -> Cultivo:
        cultivos = self._load()
        if any(c.nombre_cultivo == cultivo.nombre_cultivo and c.variedad == cultivo.variedad for c in cultivos):
            raise CultivoYaExiste(cultivo.clave)
        cultivos.append(cultivo)
        self._save(cultivos)
        return cultivo

    async def eliminar(self, nombre_cultivo: str, variedad: str = "") -> bool:
        cultivos = self._load()
        nuevos = [c for c in cultivos if not (c.nombre_cultivo == nombre_cultivo and c.variedad == variedad)]
        if len(nuevos) == len(cultivos):
            raise CultivoNoEncontrado(f"{nombre_cultivo}::{variedad}")
        self._save(nuevos)
        return True
