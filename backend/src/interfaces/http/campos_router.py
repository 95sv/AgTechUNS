"""
Router de Campos y su jerarquía anidada de Parcelas y Analítica.

Estructura de rutas (conforme YAML Entrega 4):
  GET  /campos                                                     → listar campos
  POST /campos                                                     → crear campo
  DELETE /campos/{nombre_campo}                                    → eliminar campo
  GET  /campos/{nombre_campo}/parcelas                             → listar parcelas del campo
  POST /campos/{nombre_campo}/parcelas                             → crear parcela en campo
  DELETE /campos/{nombre_campo}/parcelas/{nombre_parcela}          → eliminar parcela
  GET  /campos/{nombre_campo}/parcelas/{nombre_parcela}/recomendaciones  → alertas analíticas (CU-05)
  GET  /campos/{nombre_campo}/parcelas/{nombre_parcela}/predicciones     → predicciones (CU-06, stub)
"""
from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException, Query, status

from src.domain.entities.campo import Campo
from src.domain.entities.parcela import Parcela
from src.infrastructure.persistence.json_campo_repository import (
    JsonCampoRepository, CampoYaExiste, CampoNoEncontrado,
)
from src.infrastructure.persistence.json_parcela_repository import (
    JsonParcelaRepository, ParcelaYaExiste, ParcelaNoEncontrada,
)
from src.application.evaluate_analytics import EvaluateAnalytics
from src.interfaces.http.auth_dependency import require_admin
from src.interfaces.http.dependencies import (
    get_campo_repo, get_parcela_repo, get_evaluate_analytics_use_case,
)
from src.interfaces.http._pagination import paginar

router = APIRouter(prefix="/campos", tags=["Campos y Parcelas"])


# ── CAMPOS ──────────────────────────────────────────────────────────────────

@router.get("")
async def listar_campos(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    repo: JsonCampoRepository = Depends(get_campo_repo),
) -> dict:
    campos = await repo.listar()
    return paginar([c.model_dump() for c in campos], page, limit)


@router.post("", status_code=status.HTTP_201_CREATED)
async def crear_campo(
    campo: Campo,
    repo: JsonCampoRepository = Depends(get_campo_repo),
    _: dict = Depends(require_admin),
) -> Campo:
    try:
        return await repo.crear(campo)
    except CampoYaExiste:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="El campo ya existe")


@router.delete("/{nombre_campo}", status_code=status.HTTP_204_NO_CONTENT, response_model=None)
async def eliminar_campo(
    nombre_campo: str,
    repo: JsonCampoRepository = Depends(get_campo_repo),
    _: dict = Depends(require_admin),
) -> None:
    try:
        await repo.eliminar(nombre_campo)
    except CampoNoEncontrado:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Campo no encontrado")


# ── PARCELAS (anidadas bajo /campos/{nombre_campo}) ──────────────────────────

@router.get("/{nombre_campo}/parcelas")
async def listar_parcelas_de_campo(
    nombre_campo: str,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    parcelas_repo: JsonParcelaRepository = Depends(get_parcela_repo),
    campos_repo: JsonCampoRepository = Depends(get_campo_repo),
) -> dict:
    campos = await campos_repo.listar()
    if not any(c.nombre_campo == nombre_campo for c in campos):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Campo no encontrado")
    todas = await parcelas_repo.listar()
    del_campo = [p.model_dump() for p in todas if p.nombre_campo == nombre_campo]
    return paginar(del_campo, page, limit)


@router.post("/{nombre_campo}/parcelas", status_code=status.HTTP_201_CREATED)
async def crear_parcela_en_campo(
    nombre_campo: str,
    parcela: Parcela,
    parcelas_repo: JsonParcelaRepository = Depends(get_parcela_repo),
    campos_repo: JsonCampoRepository = Depends(get_campo_repo),
    _: dict = Depends(require_admin),
) -> Parcela:
    campos = await campos_repo.listar()
    if not any(c.nombre_campo == nombre_campo for c in campos):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Campo no encontrado")
    parcela_con_campo = parcela.model_copy(update={"nombre_campo": nombre_campo})
    try:
        return await parcelas_repo.crear(parcela_con_campo)
    except ParcelaYaExiste as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))


@router.delete("/{nombre_campo}/parcelas/{nombre_parcela}", status_code=status.HTTP_204_NO_CONTENT, response_model=None)
async def eliminar_parcela_de_campo(
    nombre_campo: str,
    nombre_parcela: str,
    parcelas_repo: JsonParcelaRepository = Depends(get_parcela_repo),
    _: dict = Depends(require_admin),
) -> None:
    try:
        await parcelas_repo.eliminar(nombre_parcela)
    except ParcelaNoEncontrada:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Parcela no encontrada")


# ── RECOMENDACIONES (CU-05: alertas tiempo real) ─────────────────────────────

@router.get("/{nombre_campo}/parcelas/{nombre_parcela}/recomendaciones")
async def obtener_recomendaciones(
    nombre_campo: str,
    nombre_parcela: str,
    parcelas_repo: JsonParcelaRepository = Depends(get_parcela_repo),
    use_case: EvaluateAnalytics = Depends(get_evaluate_analytics_use_case),
) -> dict:
    todas = await parcelas_repo.listar()
    parcela = next(
        (p for p in todas if p.nombre_parcela == nombre_parcela and p.nombre_campo == nombre_campo),
        None,
    )
    if parcela is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Parcela '{nombre_parcela}' no encontrada en campo '{nombre_campo}'",
        )

    resultado = await use_case.evaluar_parcela(parcela.model_dump())

    alertas = [
        {
            "tipo": "ALERTA_TIEMPO_REAL",
            "subtipo": a["tipo"],
            "severidad": a["severidad"],
            "fecha_emision": a["fecha_generacion"],
            "mensaje": a["mensaje"],
            "nombre_parcela": nombre_parcela,
        }
        for a in resultado["alertas_generadas"]
    ]

    return {
        "data": alertas,
        "pagination": {"page": 1, "limit": 20, "total": len(alertas), "total_pages": 1},
    }


# ── PREDICCIONES (CU-06: batch, stub) ────────────────────────────────────────

@router.get("/{nombre_campo}/parcelas/{nombre_parcela}/predicciones")
async def obtener_predicciones(
    nombre_campo: str,
    nombre_parcela: str,
) -> dict:
    return {
        "data": [],
        "pagination": {"page": 1, "limit": 20, "total": 0, "total_pages": 0},
        "mensaje": "Módulo de predicciones batch en desarrollo (CU-06).",
    }
