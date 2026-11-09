from datetime import datetime, timezone

# Umbrales preliminares para probar el prototipo; validar en el aula real.
THRESHOLDS = {
    "co2_high_ppm": 1000,
    "temperature_high_c": 26.0,
    "noise_high_db": 65.0,
    "illuminance_low_lux": 300.0,
}


def evaluate_events(telemetry: dict) -> list[dict]:
    events = []
    now = datetime.now(timezone.utc).isoformat()
    co2 = telemetry["air_quality"].get("co2_ppm")
    temp = telemetry["environment"].get("temperature_c")
    noise = telemetry["acoustic"].get("sound_level_db")
    lux = telemetry["illumination"].get("illuminance_lux")
    occupied = telemetry["occupancy"].get("presence_detected")

    if co2 is not None and co2 > THRESHOLDS["co2_high_ppm"]:
        events.append({"code": "co2_high", "title": "CO₂ elevado",
            "description": "La concentración supera el umbral preliminar configurado.",
            "severity": "warning", "value": round(co2, 1), "unit": "ppm", "timestamp": now})
    if temp is not None and temp > THRESHOLDS["temperature_high_c"]:
        events.append({"code": "temperature_high", "title": "Temperatura elevada",
            "description": "La temperatura supera el umbral preliminar configurado.",
            "severity": "warning", "value": round(temp, 1), "unit": "°C", "timestamp": now})
    if noise is not None and noise > THRESHOLDS["noise_high_db"]:
        events.append({"code": "noise_high", "title": "Actividad acústica elevada",
            "description": "El nivel acústico estimado supera el umbral de demostración.",
            "severity": "warning", "value": round(noise, 1), "unit": "dB", "timestamp": now})
    if lux is not None and lux < THRESHOLDS["illuminance_low_lux"] and occupied is True:
        events.append({"code": "low_illuminance", "title": "Iluminación baja con ocupación",
            "description": "La iluminancia está bajo el umbral preliminar mientras hay ocupación.",
            "severity": "info", "value": round(lux, 1), "unit": "lux", "timestamp": now})
    return events
