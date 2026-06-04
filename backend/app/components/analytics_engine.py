"""
Analytics Engine
----------------
Motor de analítica batch que se ejecuta periódicamente (por defecto a las 02:00 UTC).
Implementa la Alternativa C documentada en el Informe de Viabilidad:
  Motor de reglas simplificado (lógica de umbrales condicionales).

Flujo por parcela:
  1. Obtiene sensores activos desde PostgreSQL.
  2. Calcula promedios de las últimas 24h desde InfluxDB.
  3. Evalúa las reglas configuradas por el Administrador.
  4. Si se cruza un umbral → genera Predicción + Alerta + notificación.
"""
import logging
from datetime import datetime, timedelta

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import AsyncSessionLocal
from app.repositories import relational as repo
from app.repositories.timeseries import TimeSeriesRepository
from app.components.notification import NotificationService

logger = logging.getLogger(__name__)


FORMULA_EVALUATORS = {
    "humedad_promedio_menor_que": lambda promedios, umbral: (
        promedios.get("valor_humedad", 100.0) < umbral
    ),
    "temperatura_menor_que": lambda promedios, umbral: (
        promedios.get("valor_temperatura", 20.0) < umbral
    ),
    "temperatura_mayor_que": lambda promedios, umbral: (
        promedios.get("valor_temperatura", 20.0) > umbral
    ),
    "ph_fuera_de_rango": lambda promedios, umbral: (
        abs(promedios.get("valor_ph", 7.0) - 7.0) > umbral
    ),
}


def _evaluar_regla(formula: str, umbral: float, promedios: dict) -> bool:
    evaluator = FORMULA_EVALUATORS.get(formula)
    if evaluator is None:
        logger.warning("Fórmula desconocida: %s", formula)
        return False
    return evaluator(promedios, umbral)


class AnalyticsEngine:
    """Motor de analítica con scheduler APScheduler."""

    def __init__(self):
        self._scheduler = AsyncIOScheduler()
        self._ts_repo = TimeSeriesRepository()
        self._notif = NotificationService()

    def start_scheduler(self) -> None:
        self._scheduler.add_job(
            self.run_batch,
            "cron",
            hour=settings.analytics_batch_hour,
            minute=settings.analytics_batch_minute,
            id="analytics_batch",
        )
        self._scheduler.start()
        logger.info(
            "Analytics Engine scheduler arrancado (cron %02d:%02d UTC)",
            settings.analytics_batch_hour,
            settings.analytics_batch_minute,
        )

    def stop_scheduler(self) -> None:
        self._scheduler.shutdown(wait=False)

    async def run_batch(self) -> None:
        """Ejecuta el ciclo completo de analítica para todas las parcelas."""
        inicio = datetime.utcnow()
        logger.info("Analytics Engine: iniciando batch %s", inicio.isoformat())

        async with AsyncSessionLocal() as db:
            eb = await repo.create_ejecucion_batch(db, inicio)
            try:
                parcelas = await repo.get_parcelas(db)
                for parcela in parcelas:
                    await self._procesar_parcela(db, parcela.nombre_parcela, parcela.nombre_campo, inicio)
                await repo.finish_ejecucion_batch(db, eb, "completado")
            except Exception as exc:
                logger.error("Error en batch: %s", exc)
                await repo.finish_ejecucion_batch(db, eb, "error")

        logger.info("Analytics Engine: batch finalizado en %.1f s", (datetime.utcnow() - inicio).total_seconds())

    async def _procesar_parcela(
        self, db: AsyncSession, nombre_parcela: str, nombre_campo: str, inicio: datetime
    ) -> None:
        sensores_parcela = await repo.get_sensores_parcela(db, nombre_parcela)
        if not sensores_parcela:
            return

        sensor_ids = [sp.nombre_codigo_sensor for sp in sensores_parcela]
        promedios_por_sensor = await self._ts_repo.get_promedios_diarios(sensor_ids, horas=24)

        if not promedios_por_sensor:
            return

        # Promedio global de la parcela (media de todos los sensores)
        promedios_parcela: dict[str, float] = {}
        for campo_metrica in ("valor_temperatura", "valor_humedad", "valor_ph"):
            valores = [
                s[campo_metrica]
                for s in promedios_por_sensor.values()
                if campo_metrica in s
            ]
            if valores:
                promedios_parcela[campo_metrica] = sum(valores) / len(valores)

        # Evaluar reglas del campo
        reglas = await repo.get_reglas(db, nombre_campo=nombre_campo)
        for regla in reglas:
            if _evaluar_regla(regla.formula, regla.umbral, promedios_parcela):
                await self._generar_alerta_prediccion(
                    db, regla, promedios_parcela, nombre_parcela, inicio
                )

    async def _generar_alerta_prediccion(
        self,
        db: AsyncSession,
        regla,
        promedios: dict,
        nombre_parcela: str,
        inicio: datetime,
    ) -> None:
        fecha_fin = inicio + timedelta(hours=24)
        resultado = (
            f"Umbral cruzado por regla '{regla.nombre_regla}': "
            f"{regla.descripcion_regla or regla.formula} "
            f"(umbral={regla.umbral}, "
            f"temp={promedios.get('valor_temperatura', 'N/D'):.1f}°C, "
            f"hum={promedios.get('valor_humedad', 'N/D'):.1f}%)"
        )

        await repo.create_prediccion(
            db,
            resultado=resultado,
            fecha_ini=inicio - timedelta(hours=24),
            fecha_fin=fecha_fin,
            nombre_parcela=nombre_parcela,
            fecha_batch=inicio,
        )

        # Recuperar usuario responsable del campo
        campo = (await repo.get_parcela(db, nombre_parcela)).nombre_campo
        from sqlalchemy import select
        from app.models.relational import UsuarioRolCampo
        from app.database import AsyncSessionLocal
        result = await db.execute(
            select(UsuarioRolCampo).where(UsuarioRolCampo.nombre_campo == campo).limit(1)
        )
        urc = result.scalar_one_or_none()
        email_resp = urc.email_usuario if urc else "admin@agtech.com"

        alerta = await repo.create_alerta(db, resultado, nombre_parcela, email_resp)
        logger.info("Alerta generada: parcela=%s, regla=%s", nombre_parcela, regla.nombre_regla)

        await self._notif.enviar_alerta(email_resp, resultado, nombre_parcela)
