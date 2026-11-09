# Contrato JSON — L-419

`arduino_output_example.json` muestra un mensaje completo; `telemetry.schema.json` define el contrato.

- El ESP32 debe emitir **un objeto JSON completo por línea** (NDJSON).
- No mezclar mensajes de depuración con el puerto Serial.
- Mantener todas las claves aunque un sensor no esté conectado.
- Sensor no disponible: `available: false` y mediciones `null`.
- `sequence` aumenta en cada mensaje.
- `uptime_ms` mide el tiempo desde el arranque.
- `timestamp_utc` puede ser `null` hasta sincronizar el reloj.
- `thermal.frame_tenths_c` contiene exactamente 768 valores en orden por filas.
- Cada píxel térmico se expresa en décimas de °C: `251` equivale a `25.1 °C`.
- `estimated_people` es una estimación de software, no una lectura directa del MLX90640.
- `sound_level_db` solo debe llenarse con dB calibrados; RMS puede transmitirse por separado.

Sensores: BME280, MH-Z19B, INMP441, BH1750 y MLX90640. El ESP32 es el nodo de adquisición.
Los eventos los deriva el backend a partir de las mediciones; no forman parte del mensaje del sensor.
