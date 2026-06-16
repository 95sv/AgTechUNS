"""
Dependencias compartidas de FastAPI: ensamblan adapters concretos y los
inyectan en los casos de uso. Acá vive el "wiring" de la arquitectura.
"""
from fastapi import Depends

from src.application.evaluate_analytics import EvaluateAnalytics
from src.application.authenticate_user import AuthenticateUser
from src.infrastructure.persistence.influxdb_repository import InfluxDBRepository
from src.infrastructure.persistence.mock_user_repository import MockUserRepository
from src.infrastructure.persistence.json_parcela_repository import JsonParcelaRepository
from src.infrastructure.external.gateway_client import ExternalGatewayClient


async def get_time_series_repo() -> InfluxDBRepository:
    repo = InfluxDBRepository()
    await repo.connect()
    try:
        yield repo
    finally:
        await repo.close()


def get_weather_client() -> ExternalGatewayClient:
    return ExternalGatewayClient()


def get_user_repo() -> MockUserRepository:
    return MockUserRepository()


def get_parcela_repo() -> JsonParcelaRepository:
    return JsonParcelaRepository()


def get_evaluate_analytics_use_case(
    ts: InfluxDBRepository = Depends(get_time_series_repo),
    w: ExternalGatewayClient = Depends(get_weather_client),
) -> EvaluateAnalytics:
    return EvaluateAnalytics(time_series=ts, weather=w)


def get_authenticate_use_case(
    users: MockUserRepository = Depends(get_user_repo),
) -> AuthenticateUser:
    return AuthenticateUser(user_repo=users)
