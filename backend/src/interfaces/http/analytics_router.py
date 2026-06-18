"""
Router de Analytics — endpoint interno usado por el dashboard Next.js.

El contrato público (YAML Entrega 4) expone analítica vía:
  GET /campos/{campo}/parcelas/{parcela}/recomendaciones

Este router mantiene POST /analytics/evaluar como endpoint de conveniencia
que evalúa TODAS las parcelas y agrega los resultados en el formato que
consume el panel de Analytics del dashboard.
"""
from fastapi import APIRouter, Depends

from src.application.evaluate_analytics import EvaluateAnalytics
from src.infrastructure.persistence.json_parcela_repository import JsonParcelaRepository
from src.interfaces.http.dependencies import (
    get_evaluate_analytics_use_case,
    get_parcela_repo,
)

router = APIRouter(prefix="/analytics", tags=["Analytics Engine"])


@router.post("/evaluar")
async def evaluar_todas(
    use_case: EvaluateAnalytics = Depends(get_evaluate_analytics_use_case),
    parcelas_repo: JsonParcelaRepository = Depends(get_parcela_repo),
) -> dict:
    parcelas = await parcelas_repo.listar()
    resultado = await use_case.evaluar_parcelas([p.model_dump() for p in parcelas])

    alertas_flat = [
        {
            "tipo": "ALERTA_TIEMPO_REAL",
            "subtipo": a["tipo"],
            "severidad": a["severidad"],
            "fecha_emision": a["fecha_generacion"],
            "mensaje": a["mensaje"],
            "nombre_parcela": d["nombre_parcela"],
        }
        for d in resultado["detalle"]
        for a in d["alertas_generadas"]
    ]

    return {
        "total_alertas": len(alertas_flat),
        "detalle": alertas_flat,
    }
