"""
Router HTTP del Analytics Engine. Adapter primario que dispara manualmente
el caso de uso EvaluateAnalytics (equivalente al Batch Scheduler nocturno
del CU-06 mientras la programación automática queda como trabajo futuro).
"""
from __future__ import annotations
from fastapi import APIRouter, Depends

from src.application.evaluate_analytics import EvaluateAnalytics
from src.interfaces.http.dependencies import get_evaluate_analytics_use_case

router = APIRouter(prefix="/analytics", tags=["Analytics Engine"])

PARCELAS_DEMO = [
    {"nombre_parcela": "Parcela-Norte", "nombre_codigo_sensor": "SN-001", "lat": -38.71, "lon": -62.27},
    {"nombre_parcela": "Parcela-Sur",   "nombre_codigo_sensor": "SN-002", "lat": -38.75, "lon": -62.30},
]


@router.post("/evaluar")
async def evaluar(
    use_case: EvaluateAnalytics = Depends(get_evaluate_analytics_use_case),
) -> dict:
    return await use_case.evaluar_parcelas(PARCELAS_DEMO)
