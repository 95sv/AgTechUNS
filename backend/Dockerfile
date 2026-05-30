# Imagen del backend AgTechUNS.
# La misma imagen sirve para dos procesos: el servidor HTTP FastAPI (default)
# y el worker de ingesta MQTT (override del CMD en docker-compose).

FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
        gcc \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
