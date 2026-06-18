"""
Helper compartido: lectura y escritura de JSON.

Implementación simple (overwrite directo) en vez de atomic write con rename,
porque `os.replace()` sobre archivos bind-mounteados de Docker falla con
"Device or resource busy". Para el alcance académico el riesgo de un write
parcial ante un crash es aceptable.
"""
from __future__ import annotations
import json
from pathlib import Path


def leer_json(path: Path) -> dict:
    if not path.exists():
        return {}
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def escribir_json(path: Path, datos: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=2)
