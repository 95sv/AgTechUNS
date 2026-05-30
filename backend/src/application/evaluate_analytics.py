"""
Caso de uso: Evaluar el Analytics Engine sobre una o más parcelas.

Es el corazón de la inteligencia del sistema: construye el contexto
cruzando datos de las dos fuentes (TimeSeriesPort + WeatherPort) y
aplica las reglas agronómicas del dominio.
"""
from __future__ import annotations
import logging
from typing import Any

from src.domain.entities.alerta import Alerta
from src.domain.ports.time_series_port import TimeSeriesPort
from src.domain.ports.weather_port import WeatherPort
from src.domain.rules.reglas_agronomicas import REGLAS

_log = logging.getLogger("evaluate_analytics")


class EvaluateAnalytics:
    def __init__(self, time_series: TimeSeriesPort, weather: WeatherPort):
        self._ts = time_series
        self._weather = weather

    async def _construir_contexto(self, parcela: dict) -> tuple[dict[str, Any], list[str]]:
        ctx: dict[str, Any] = {"nombre_parcela": parcela["nombre_parcela"]}
        fuentes_caidas: list[str] = []
        try:
            ctx["humedad_promedio_24h"] = await self._ts.promedio_diario(
                parcela["nombre_codigo_sensor"], "valor_humedad"
            )
            ctx["temperatura_promedio_24h"] = await self._ts.promedio_diario(
                parcela["nombre_codigo_sensor"], "valor_temperatura"
            )
        except Exception as exc:
            _log.warning("InfluxDB inaccesible: %s", exc)
            fuentes_caidas.append("influxdb")
        try:
            clima = await self._weather.fetch_weather(parcela["lat"], parcela["lon"])
            ctx["temp_ambiente_actual"] = float(clima.get("temperature"))
        except Exception as exc:
            _log.warning("External Gateway inaccesible: %s", exc)
            fuentes_caidas.append("external_gateway")
        return ctx, fuentes_caidas

    async def evaluar_parcela(self, parcela: dict) -> dict:
        ctx, caidas = await self._construir_contexto(parcela)
        alertas: list[Alerta] = []
        for regla in REGLAS:
            try:
                resultado = regla(ctx)
                if resultado is not None:
                    alertas.append(resultado)
            except Exception as exc:
                _log.error("Regla %s falló: %s", regla.__name__, exc)
        return {
            "nombre_parcela": parcela["nombre_parcela"],
            "contexto": ctx,
            "fuentes_caidas": caidas,
            "alertas_generadas": [a.model_dump(mode="json") for a in alertas],
        }

    async def evaluar_parcelas(self, parcelas: list[dict]) -> dict:
        detalle = [await self.evaluar_parcela(p) for p in parcelas]
        return {
            "parcelas_evaluadas": len(parcelas),
            "total_alertas": sum(len(d["alertas_generadas"]) for d in detalle),
            "detalle": detalle,
        }
