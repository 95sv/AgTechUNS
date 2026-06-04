from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # PostgreSQL
    database_url: str = "postgresql+asyncpg://agtech:agtech_pass@localhost:5432/agtech_db"

    # InfluxDB
    influxdb_url: str = "http://localhost:8086"
    influxdb_token: str = "agtech-super-secret-token"
    influxdb_org: str = "agtech_org"
    influxdb_bucket: str = "agtech_data"

    # MQTT
    mqtt_broker_host: str = "localhost"
    mqtt_broker_port: int = 1883

    # JWT
    secret_key: str = "cambia-esta-clave-en-produccion"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    # Weather API (Open-Meteo — no requiere key)
    weather_api_url: str = "https://api.open-meteo.com/v1/forecast"

    # SendGrid
    sendgrid_api_key: str = "SG.placeholder"
    sendgrid_from_email: str = "agtech@agtech-uns.com"

    # Google Earth Engine
    gee_service_account: str = ""
    gee_key_file: str = "gee_key.json"

    # Analytics Engine batch schedule
    analytics_batch_hour: int = 2
    analytics_batch_minute: int = 0


settings = Settings()
