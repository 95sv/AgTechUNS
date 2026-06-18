"""
Helper compartido: lectura y escritura atómica de JSON.
Usado por todos los repositorios JSON. Centraliza el manejo de archivo y
el atomic write (escribe en tmp + rename) para evitar archivos corruptos.
"""
from __future__ import annotations
import json
import os
import tempfile
from pathlib import Path


def leer_json(path: Path) -> dict:
    if not path.exists():
        return {}
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def escribir_json(path: Path, datos: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    dir_destino = str(path.parent)
    with tempfile.NamedTemporaryFile(
        mode="w", encoding="utf-8", dir=dir_destino, delete=False, suffix=".tmp"
    ) as tmp:
        json.dump(datos, tmp, ensure_ascii=False, indent=2)
        tmp_path = tmp.name
    os.replace(tmp_path, path)
