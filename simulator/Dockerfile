# Imagen del sensor IoT simulado.
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY sensor_simulator.py .
CMD ["python", "sensor_simulator.py", "--sensores", "SN-001", "SN-002", "--intervalo", "3"]
