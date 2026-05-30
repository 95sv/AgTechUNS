# Sensor IoT Simulado

Genera lecturas sintéticas de humedad y temperatura para dos sensores
(`SN-001` en Parcela-Norte, `SN-002` en Parcela-Sur) y las publica en el
broker MQTT al tópico `agtech/sensores/<codigo_sensor>`.

Reemplaza a sensores físicos durante el desarrollo. En un escenario
productivo, esta misma posición en la arquitectura la ocuparían los
dispositivos reales publicando al mismo tópico.

Las lecturas las consume el `ingestion_worker` del backend.
