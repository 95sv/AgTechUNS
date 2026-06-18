import logging, os
from pathlib import Path

from src.domain.entities.campo import Campo
from src.infrastructure.persistence._json_store import leer_json, escribir_json

_log = logging.getLogger("json_campo_repository")
DEFAULT_PATH = "/app/config/campos.json"


class CampoYaExiste(Exception): pass
class CampoNoEncontrado(Exception): pass


class JsonCampoRepository:
    def __init__(self, path: str | None = None):
        self._path = Path(path or os.getenv("CAMPOS_CONFIG_PATH", DEFAULT_PATH))

    def _load(self) -> list[Campo]:
        data = leer_json(self._path)
        return [Campo(**c) for c in data.get("campos", [])]

    def _save(self, campos: list[Campo]) -> None:
        escribir_json(self._path, {"campos": [c.model_dump() for c in campos]})

    async def listar(self) -> list[Campo]:
        return self._load()

    async def crear(self, campo: Campo) -> Campo:
        campos = self._load()
        if any(c.nombre_campo == campo.nombre_campo for c in campos):
            raise CampoYaExiste(campo.nombre_campo)
        campos.append(campo)
        self._save(campos)
        return campo

    async def eliminar(self, nombre_campo: str) -> bool:
        campos = self._load()
        nuevos = [c for c in campos if c.nombre_campo != nombre_campo]
        if len(nuevos) == len(campos):
            raise CampoNoEncontrado(nombre_campo)
        self._save(nuevos)
        return True
