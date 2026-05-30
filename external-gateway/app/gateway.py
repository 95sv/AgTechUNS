from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
import asyncio
import time

import ee
import httpx

from .config import settings
from .models import SatelliteResponse, WeatherResponse


class SatelliteDataUnavailable(RuntimeError):
    pass


class WeatherDataUnavailable(RuntimeError):
    pass


class ExternalDataGateway:
    def __init__(self, weather_url: str = settings.open_meteo_url):
        self.weather_url = weather_url
        self._gee_initialized = False

    def _initialize_gee(self) -> None:
        if self._gee_initialized:
            return

        credentials_path = Path(settings.gee_credentials_file)
        if not credentials_path.exists():
            raise RuntimeError(
                f"Earth Engine credentials file not found: {credentials_path}"
            )

        if not settings.gee_project_id:
            raise SatelliteDataUnavailable(
                "Earth Engine project id is not configured. Set GEE_PROJECT_ID or keep project_id inside service_account.json."
            )

        credentials = ee.ServiceAccountCredentials(
            self._service_account_email(),
            str(credentials_path),
        )
        ee.Initialize(credentials, project=settings.gee_project_id)
        self._gee_initialized = True

    def _service_account_email(self) -> str:
        credentials_path = Path(settings.gee_credentials_file)
        data = credentials_path.read_text(encoding="utf-8")
        import json

        parsed = json.loads(data)
        client_email = parsed.get("client_email")
        if not client_email:
            raise RuntimeError("service_account.json is missing client_email")
        return client_email

    async def fetch_weather(self, lat: float, lon: float) -> WeatherResponse:
        async with httpx.AsyncClient(timeout=httpx.Timeout(15.0)) as client:
            resp = await self._get_with_retries(
                client,
                self.weather_url,
                params={"latitude": lat, "longitude": lon, "current_weather": True},
            )

            data = resp.json().get("current_weather")
            if not data:
                raise WeatherDataUnavailable("Provider returned unexpected payload: missing current_weather")

            return WeatherResponse(
                temperature=float(data["temperature"]),
                timestamp=str(data["time"]),
                latitude=float(lat),
                longitude=float(lon),
                provider="open-meteo",
            )

    async def _get_with_retries(self, client: httpx.AsyncClient, url: str, params: dict | None = None, retries: int = 3) -> httpx.Response:
        last_exc: Exception | None = None
        for attempt in range(1, retries + 1):
            try:
                resp = await client.get(url, params=params)
                # retry on server errors
                if 500 <= resp.status_code < 600:
                    last_exc = httpx.HTTPStatusError("server error", request=resp.request, response=resp)
                    raise last_exc
                resp.raise_for_status()
                return resp
            except (httpx.RequestError, httpx.HTTPStatusError) as exc:
                last_exc = exc
                if attempt == retries:
                    raise
                backoff = 0.5 * (2 ** (attempt - 1))
                await asyncio.sleep(backoff)


    async def fetch_satellite_indices(
        self, lat: float, lon: float, parcel_id: int
    ) -> SatelliteResponse:
        return await asyncio.to_thread(
            self._fetch_satellite_indices_sync, lat, lon, parcel_id
        )

    def _fetch_satellite_indices_sync(
        self, lat: float, lon: float, parcel_id: int
    ) -> SatelliteResponse:
        self._initialize_gee()

        point = ee.Geometry.Point([lon, lat])
        end_date = datetime.now(timezone.utc)
        start_date = end_date - timedelta(days=30)

        collection = (
            ee.ImageCollection(settings.gee_collection_name)
            .filterBounds(point)
            .filterDate(start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"))
            .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", 40))
            .sort("CLOUDY_PIXEL_PERCENTAGE")
        )

        if collection.size().getInfo() == 0:
            raise SatelliteDataUnavailable(
                "No Sentinel-2 images were found for that location and date range."
            )

        image = ee.Image(collection.first())
        indices = (
            image.normalizedDifference(["B8", "B4"]).rename("NDVI")
            .addBands(image.normalizedDifference(["B8", "B11"]).rename("NDMI"))
        )

        values = indices.reduceRegion(
            reducer=ee.Reducer.first(),
            geometry=point,
            scale=20,
            bestEffort=True,
            maxPixels=1_000_000,
        ).getInfo()

        ndvi = values.get("NDVI")
        ndmi = values.get("NDMI")

        if ndvi is None or ndmi is None:
            raise SatelliteDataUnavailable("Could not compute satellite indices for the selected point.")

        return SatelliteResponse(
            ndvi=float(ndvi),
            ndmi=float(ndmi),
            parcel_id=parcel_id,
            computed_at=datetime.now(timezone.utc).isoformat(),
            latency_days=5,
        )