"""
Notification Component
----------------------
Despacha alertas críticas vía SendGrid (email).
Si la API key no está configurada, registra la alerta en el log (modo desarrollo).
"""
import logging
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from app.config import settings

logger = logging.getLogger(__name__)


class NotificationService:

    def __init__(self):
        self._api_key = settings.sendgrid_api_key
        self._from_email = settings.sendgrid_from_email
        self._enabled = not self._api_key.startswith("SG.placeholder")

    async def enviar_alerta(self, email_destino: str, mensaje: str, nombre_parcela: str) -> None:
        asunto = f"[AgTechUNS] Alerta en parcela {nombre_parcela}"
        cuerpo = (
            f"<h2>Alerta agroclimática</h2>"
            f"<p><strong>Parcela:</strong> {nombre_parcela}</p>"
            f"<p><strong>Detalle:</strong> {mensaje}</p>"
            f"<hr><small>AgTechUNS — Sistema de Monitoreo Agrícola</small>"
        )

        if not self._enabled:
            logger.info(
                "[NOTIF SIMULADA] Para: %s | Asunto: %s | Cuerpo: %s",
                email_destino, asunto, mensaje,
            )
            return

        try:
            mail = Mail(
                from_email=self._from_email,
                to_emails=email_destino,
                subject=asunto,
                html_content=cuerpo,
            )
            sg = SendGridAPIClient(self._api_key)
            response = sg.send(mail)
            logger.info("Email enviado a %s (status %s)", email_destino, response.status_code)
        except Exception as exc:
            logger.error("Error enviando email a %s: %s", email_destino, exc)
