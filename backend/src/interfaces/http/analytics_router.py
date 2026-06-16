"""
Router HTTP del Analytics Engine. Adapter primario que dispara manualmente
el caso de uso EvaluateAnalytics sobre todas las parcelas configuradas.
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
async def evaluar(
    use_case: EvaluateAnalytics = Depends(get_evaluate_analytics_use_case),
    parcelas_repo: JsonParcelaRepository = Depends(get_parcela_repo),
) -> dict:
    parcelas = await parcelas_repo.listar()
    return await use_case.evaluar_parcelas([p.model_dump() for p in parcelas])
