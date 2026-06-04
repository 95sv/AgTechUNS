"""
Mapa endpoint — CU-01: Visualizar mapa satelital y estado de parcelas.
Consolida datos satelitales + lecturas de sensores + pronóstico del clima.
"""
from __future__ import annotations

import json
from fastapi import APIRouter, HTTPException
from app.api.deps import DB, CurrentUser
from app.components.sensor_simulator import SensorSimulator
from app.repositories import relational as repo
from app.repositories.timeseries import TimeSeriesRepository
from app.components.external_gateway import ExternalDataGateway

router = APIRouter()
ts_repo = TimeSeriesRepository()
gateway = ExternalDataGateway()
sensor_simulator = SensorSimulator()


def _calcular_centro_geojson(geo: dict) -> tuple[float | None, float | None]:
    if geo.get("type") == "Polygon":
        coords = geo.get("coordinates", [[]])[0]
        if not coords:
            return None, None
        lat = sum(c[1] for c in coords) / len(coords)
        lon = sum(c[0] for c in coords) / len(coords)
        return lat, lon
    if geo.get("type") == "Point":
        lon, lat = geo.get("coordinates", [None, None])
        return lat, lon
    return None, None


def _resumen_lecturas(lecturas: dict[str, dict]) -> dict[str, float | None]:
    temperaturas = [l.get("temperatura") for l in lecturas.values() if l.get("temperatura") is not None]
    humedades = [l.get("humedad") for l in lecturas.values() if l.get("humedad") is not None]
    phs = [l.get("ph") for l in lecturas.values() if l.get("ph") is not None]
    return {
        "temperatura_promedio": round(sum(temperaturas) / len(temperaturas), 1) if temperaturas else None,
        "humedad_promedio": round(sum(humedades) / len(humedades), 1) if humedades else None,
        "ph_promedio": round(sum(phs) / len(phs), 1) if phs else None,
    }


def _ordenar_lecturas(lecturas: dict[str, dict]) -> dict[str, dict]:
    return dict(sorted(lecturas.items(), key=lambda item: item[0]))


@router.get("/campos/{nombre_campo}")
async def mapa_campo(nombre_campo: str, db: DB, _: CurrentUser):
    """
    Retorna la vista consolidada del mapa para un campo:
    - Parcelas con coordenadas
    - Última lectura de cada sensor activo
    - Índices satelitales (NDVI/NDMI) más recientes
    Tiempo máximo: 4 s (CU-01).
    """
    campo = await repo.get_campo(db, nombre_campo)
    if not campo:
        raise HTTPException(404, "Campo no encontrado")

    parcelas = await repo.get_parcelas(db, nombre_campo=nombre_campo)
    reglas = await repo.get_reglas(db, nombre_campo=nombre_campo)
    resultado = []

    for parcela in parcelas:
        sensores_parcela = await repo.get_sensores_parcela(db, parcela.nombre_parcela)
        sensor_ids = [sp.nombre_codigo_sensor for sp in sensores_parcela]

        lecturas_recientes = {}
        for sid in sensor_ids:
            lectura = await ts_repo.get_ultima_lectura(sid)
            if lectura:
                lecturas_recientes[sid] = lectura

        imagen_pis = await repo.get_ultima_imagen_parcela(db, parcela.nombre_parcela)

        coordenadas = None
        lat, lon = None, None
        if parcela.coordenadas_parcela:
            try:
                geo = json.loads(parcela.coordenadas_parcela)
                coordenadas = geo
                lat, lon = _calcular_centro_geojson(geo)
            except (json.JSONDecodeError, KeyError, TypeError):
                pass

        clima = await gateway.get_pronostico(lat, lon, dias=3) if lat is not None and lon is not None else None

        if lecturas_recientes:
            sensores_visibles = _ordenar_lecturas(lecturas_recientes)
            resumen_sensores = _resumen_lecturas(sensores_visibles)
            origen_sensores = "real"
        else:
            simulacion = sensor_simulator.simular_parcela(
                parcela.nombre_parcela,
                lat,
                lon,
                clima=clima,
                ndvi=imagen_pis.indice_ndvi if imagen_pis else None,
                ndmi=imagen_pis.indice_ndmi if imagen_pis else None,
            )
            sensores_visibles = simulacion["sensores"]
            resumen_sensores = simulacion["resumen"]
            origen_sensores = simulacion["origen"]

        resultado.append({
            "parcela": parcela.nombre_parcela,
            "descripcion": parcela.descripcion_parcela,
            "coordenadas": coordenadas,
            "centro": {"lat": lat, "lon": lon} if lat is not None and lon is not None else None,
            "sensores": sensores_visibles,
            "sensores_resumen": resumen_sensores,
            "sensores_origen": origen_sensores,
            "satelital": {
                "ndvi": imagen_pis.indice_ndvi if imagen_pis else None,
                "ndmi": imagen_pis.indice_ndmi if imagen_pis else None,
            },
            "clima": clima,
        })

    return {
        "campo": nombre_campo,
        "descripcion": campo.descripcion_campo,
        "coordenadas": campo.coordenadas_campo,
        "reglas": [
            {
                "nombre_regla": regla.nombre_regla,
                "formula": regla.formula,
                "descripcion_regla": regla.descripcion_regla,
                "umbral": regla.umbral,
                "nombre_campo": regla.nombre_campo,
            }
            for regla in reglas
        ],
        "parcelas": resultado,
    }


@router.get("/campos/{nombre_campo}/pronostico")
async def pronostico_campo(nombre_campo: str, db: DB, _: CurrentUser, lat: float = -38.7, lon: float = -62.3, dias: int = 7):
    """
    Pronóstico meteorológico para las coordenadas del campo (Open-Meteo).
    Coordenadas por defecto: Bahía Blanca, Argentina.
    """
    data = await gateway.get_pronostico(lat, lon, dias)
    if not data:
        raise HTTPException(503, "Servicio de clima no disponible temporalmente")
    return data


@router.post("/parcelas/{nombre_parcela}/indices-satelitales")
async def actualizar_indices(nombre_parcela: str, db: DB, _: CurrentUser, lat: float = -38.7, lon: float = -62.3):
    """
    Obtiene y persiste índices NDVI/NDMI para la parcela (simulado con GEE stub).
    """
    parcela = await repo.get_parcela(db, nombre_parcela)
    if not parcela:
        raise HTTPException(404, "Parcela no encontrada")

    indices = await gateway.get_indices_satelitales(nombre_parcela, lat, lon)
    if not indices:
        raise HTTPException(503, "No se pudieron obtener índices satelitales")

    from datetime import datetime
    imagen = await repo.create_imagen_satelital(db, datetime.utcnow(), indices["fuente"])
    await repo.asignar_imagen_parcela(
        db,
        imagen.id_imagen,
        nombre_parcela,
        indices["ndvi"],
        indices["ndmi"],
    )

    return indices
