"""
Reglas agronómicas del Analytics Engine (MVP — Alternativa A del estudio de viabilidad).

Cada regla es una función PURA sin dependencias externas:
    contexto (dict)  ->  Alerta | None

Para agregar una regla nueva: definir la función con esta misma firma y
sumarla a la lista REGLAS al final del archivo.
"""
from __future__ import annotations
from typing import Optional

from src.domain.entities.alerta import Alerta

# Umbrales (en producción se moverían a la BD como entidad REGLA)
UMBRAL_HUMEDAD_BAJA = 30.0
UMBRAL_HUMEDAD_ALTA = 85.0
UMBRAL_TEMP_AMBIENTE_FRIA = 5.0
UMBRAL_TEMP_ENFERMEDAD = 20.0
UMBRAL_HUMEDAD_RIESGO_FRIO = 40.0


def regla_estres_hidrico(ctx: dict) -> Optional[Alerta]:
    """Humedad de suelo persistentemente baja en las últimas 24h."""
    h = ctx.get("humedad_promedio_24h")
    if h is None:
        return None
    if h < UMBRAL_HUMEDAD_BAJA:
        return Alerta(
            nombre_parcela=ctx["nombre_parcela"],
            tipo="estres_hidrico",
            severidad="alta",
            mensaje=f"Humedad de suelo promedio 24h: {h:.1f}% (umbral {UMBRAL_HUMEDAD_BAJA}%). Recomendado activar riego.",
            datos_evaluados={"humedad_promedio_24h": h, "umbral": UMBRAL_HUMEDAD_BAJA},
        )
    return None


def regla_condiciones_enfermedad_fungica(ctx: dict) -> Optional[Alerta]:
    """Humedad alta + temperatura cálida = riesgo de enfermedades fúngicas."""
    h = ctx.get("humedad_promedio_24h")
    t = ctx.get("temperatura_promedio_24h")
    if h is None or t is None:
        return None
    if h > UMBRAL_HUMEDAD_ALTA and t > UMBRAL_TEMP_ENFERMEDAD:
        return Alerta(
            nombre_parcela=ctx["nombre_parcela"],
            tipo="riesgo_enfermedad_fungica",
            severidad="media",
            mensaje=f"Humedad alta ({h:.1f}%) + temperatura cálida ({t:.1f}°C). Monitorear cultivos por hongos.",
            datos_evaluados={"humedad_promedio_24h": h, "temperatura_promedio_24h": t},
        )
    return None


def regla_riesgo_frio_con_sequedad(ctx: dict) -> Optional[Alerta]:
    """Cruza las dos fuentes: temperatura ambiente (gateway) + humedad de sensor (InfluxDB)."""
    ta = ctx.get("temp_ambiente_actual")
    hs = ctx.get("humedad_promedio_24h")
    if ta is None or hs is None:
        return None
    if ta < UMBRAL_TEMP_AMBIENTE_FRIA and hs < UMBRAL_HUMEDAD_RIESGO_FRIO:
        return Alerta(
            nombre_parcela=ctx["nombre_parcela"],
            tipo="riesgo_frio_con_sequedad",
            severidad="alta",
            mensaje=f"Temperatura ambiente baja ({ta:.1f}°C) y humedad de suelo reducida ({hs:.1f}%). Riesgo combinado.",
            datos_evaluados={"temp_ambiente_actual": ta, "humedad_promedio_24h": hs},
        )
    return None


REGLAS = [
    regla_estres_hidrico,
    regla_condiciones_enfermedad_fungica,
    regla_riesgo_frio_con_sequedad,
]
