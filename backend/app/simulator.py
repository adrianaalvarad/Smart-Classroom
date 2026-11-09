import math
import random
import time
from datetime import datetime, timezone


def make_frame(base_temp: float, phase: float) -> list[int]:
    """Matriz térmica sintética 32x24, ordenada por filas."""
    centers = [
        (7 + 1.5 * math.sin(phase / 9), 7, 5.5),
        (16, 10 + 1.2 * math.cos(phase / 11), 5.0),
        (25, 8, 5.8),
        (12, 18, 4.0),
    ]
    frame = []
    for row in range(24):
        for col in range(32):
            value = base_temp + 0.22 * math.sin(col / 4) + 0.16 * math.cos(row / 3)
            for cx, cy, amplitude in centers:
                distance = ((col - cx) ** 2) / 7.0 + ((row - cy) ** 2) / 5.0
                value += amplitude * math.exp(-distance)
            value += random.uniform(-0.18, 0.18)
            frame.append(round(value * 10))
    return frame


def make_telemetry(sequence: int, started_at: float) -> dict:
    elapsed = time.monotonic() - started_at
    phase = elapsed

    temperature = 24.0 + 2.5 * max(0, math.sin(phase / 35)) + random.uniform(-0.15, 0.15)
    humidity = 53 + 5 * math.sin(phase / 28) + random.uniform(-0.5, 0.5)
    pressure = 1008.5 + 0.8 * math.sin(phase / 50) + random.uniform(-0.08, 0.08)
    co2 = 760 + 520 * max(0, math.sin(phase / 24)) + random.uniform(-18, 18)
    noise_db = 51 + 19 * max(0, math.sin(phase / 17)) + random.uniform(-1.5, 1.5)
    lux = 430 + 170 * math.sin(phase / 21) + random.uniform(-12, 12)

    # Conteo sintético solo para demostrar la interfaz.
    people = max(0, min(28, round(16 + 3 * math.sin(phase / 40))))
    frame = make_frame(temperature + 0.4, phase)
    frame_c = [value / 10 for value in frame]

    return {
        "schema_version": 1,
        "device_id": "L419-ESP32-01",
        "sequence": sequence,
        "uptime_ms": int(elapsed * 1000),
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "environment": {
            "available": True, "model": "BME280",
            "temperature_c": round(temperature, 2),
            "humidity_pct": round(humidity, 2),
            "pressure_hpa": round(pressure, 2)
        },
        "air_quality": {"available": True, "model": "MH-Z19B", "co2_ppm": round(co2, 1)},
        "acoustic": {
            "available": True, "model": "INMP441",
            "rms": round(0.018 + (noise_db - 50) / 1800, 5),
            "sound_level_db": round(noise_db, 1)
        },
        "illumination": {"available": True, "model": "BH1750", "illuminance_lux": round(max(0, lux), 1)},
        "occupancy": {
            "available": True, "model": "MLX90640 + algoritmo de demostración",
            "presence_detected": people > 0, "estimated_people": people
        },
        "thermal": {
            "available": True, "frame_valid": True, "width": 32, "height": 24,
            "center_temp_c": round(sum(frame_c[i] for i in (367, 368, 399, 400)) / 4, 2),
            "mean_temp_c": round(sum(frame_c) / len(frame_c), 2),
            "min_temp_c": round(min(frame_c), 2), "max_temp_c": round(max(frame_c), 2),
            "frame_tenths_c": frame
        },
        "connectivity": {"wifi_connected": False, "rssi_dbm": None}
    }


def make_thermal_frame(sequence: int, started_at: float) -> dict:
    """Genera un fotograma térmico sintético cumpliendo el contrato v1.0."""
    elapsed = time.monotonic() - started_at
    base_temp = 24.0 + 1.8 * math.sin(elapsed / 30)
    pixels = make_frame(base_temp, elapsed)
    min_dc = min(pixels)
    max_dc = max(pixels)
    ambient_dc = round(base_temp * 10)
    return {
        "type": "thermal_frame",
        "schema_version": 1,
        "device_id": "L419-ESP32-01",
        "sequence": sequence,
        "width": 32,
        "height": 24,
        "ambient_dC": ambient_dc,
        "min_dC": min_dc,
        "max_dC": max_dc,
        "pixels_dC": pixels
    }
