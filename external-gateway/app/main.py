import httpx

from fastapi import FastAPI, HTTPException
from .gateway import ExternalDataGateway, SatelliteDataUnavailable, WeatherDataUnavailable
from .models import SatelliteResponse, WeatherResponse

app = FastAPI(title="AgTechUns - External Data Gateway")
gateway = ExternalDataGateway()

# Endpoint de Clima (el que ya te sale)
@app.get("/weather", response_model=WeatherResponse)
async def get_weather(lat: float, lon: float):
    try:
        return await gateway.fetch_weather(lat, lon)
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=502, detail=f"Weather provider error: {exc.response.status_code}")
    except httpx.RequestError as exc:
        raise HTTPException(status_code=503, detail=f"Weather provider unavailable: {exc.__class__.__name__}")
    except WeatherDataUnavailable as exc:
        raise HTTPException(status_code=502, detail=str(exc))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Endpoint de Satélite (el que te falta)
@app.get("/satellite/{parcel_id}", response_model=SatelliteResponse)
async def get_satellite(parcel_id: int, lat: float, lon: float):
    try:
        return await gateway.fetch_satellite_indices(lat, lon, parcel_id)
    except SatelliteDataUnavailable as exc:
        raise HTTPException(status_code=502, detail=str(exc))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health():
    return {"status": "ok"}