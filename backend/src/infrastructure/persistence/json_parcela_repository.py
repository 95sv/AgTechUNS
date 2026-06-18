import os, logging
from pathlib import Path

from src.domain.entities.parcela import Parcela
from src.infrastructure.persistence._json_store import leer_json, escribir_json

_log = logging.getLogger("json_parcela_repository")
DEFAULT_PATH = "/app/config/parcelas.json"

PARCELAS_FALLBACK = [
    Parcela(nombre_parcela="Parcela-Norte", nombre_campo="Campo-Demo", nombre_codigo_sensor="SN-001", lat=-38.71, lon=-62.27),
    Parcela(nombre_parcela="Parcela-Sur",   nombre_campo="Campo-Demo", nombre_codigo_sensor="SN-002", lat=-38.75, lon=-62.30),
]


class ParcelaYaExiste(Exception): pass
class ParcelaNoEncontrada(Exception): pass


class JsonParcelaRepository:
    def __init__(self, path: str | None = None):
        self._path = Path(path or os.getenv("PARCELAS_CONFIG_PATH", DEFAULT_PATH))

    def _load(self) -> list[Parcela]:
        if not self._path.exists():
            _log.warning("Archivo de parcelas no encontrado: %s. Usando fallback.", self._path)
            return list(PARCELAS_FALLBACK)
        data = leer_json(self._path)
        return [Parcela(**p) for p in data.get("parcelas", [])]

    def _save(self, parcelas: list[Parcela]) -> None:
        escribir_json(self._path, {"parcelas": [p.model_dump() for p in parcelas]})

    async def listar(self) -> list[Parcela]:
        return self._load()

    async def crear(self, parcela: Parcela) -> Parcela:
        parcelas = self._load()
        if any(p.nombre_parcela == parcela.nombre_parcela for p in parcelas):
            raise ParcelaYaExiste(parcela.nombre_parcela)
        if any(p.nombre_codigo_sensor == parcela.nombre_codigo_sensor for p in parcelas):
            raise ParcelaYaExiste(f"sensor {parcela.nombre_codigo_sensor} ya en uso")
        parcelas.append(parcela)
        self._save(parcelas)
        return parcela

    async def eliminar(self, nombre_parcela: str) -> bool:
        parcelas = self._load()
        nuevos = [p for p in parcelas if p.nombre_parcela != nombre_parcela]
        if len(nuevos) == len(parcelas):
            raise ParcelaNoEncontrada(nombre_parcela)
        self._save(nuevos)
        return True
