import asyncio
import os
import time
from collections import deque
from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from .event_engine import evaluate_events, THRESHOLDS
from .schemas import Telemetry, ThermalFrame
from .simulator import make_telemetry, make_thermal_frame
from .serial_reader import open_serial, read_json_line


DATA_SOURCE = os.getenv("DATA_SOURCE", "simulator").lower()
SERIAL_PORT = os.getenv("SERIAL_PORT", "COM6")
SERIAL_BAUD = int(os.getenv("SERIAL_BAUD", "460800"))

latest_bundle = None
latest_thermal_frame = None
last_sequence = 0
serial_connected = False
serial_message = "Simulator mode active" if DATA_SOURCE == "simulator" else "Disconnected"

history = deque(maxlen=180)
event_log = deque(maxlen=40)
previous_active_events = {}
source_error = None


class ConnectionManager:
    def __init__(self):
        self.connections = set()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.connections.add(websocket)

    def disconnect(self, websocket: WebSocket):
        self.connections.discard(websocket)

    async def broadcast(self, message: dict):
        disconnected = []
        for connection in list(self.connections):
            try:
                await connection.send_json(message)
            except Exception:
                disconnected.append(connection)
        for connection in disconnected:
            self.disconnect(connection)


manager = ConnectionManager()
thermal_manager = ConnectionManager()


async def publish_thermal_frame(frame: dict):
    global latest_thermal_frame, last_sequence
    latest_thermal_frame = frame
    last_sequence = frame.get("sequence", last_sequence)
    await thermal_manager.broadcast(frame)


async def publish_payload(raw_payload: dict):
    global latest_bundle, previous_active_events, source_error, last_sequence

    # Comprobar si el payload es directamente un thermal_frame del nuevo contrato v1.0
    if raw_payload.get("type") == "thermal_frame" or "pixels_dC" in raw_payload:
        await publish_thermal_frame(raw_payload)
        return

    # Si es el payload completo multisensor
    try:
        telemetry = Telemetry.model_validate(raw_payload).model_dump(mode="json")
    except Exception:
        # Si tiene pixels_dC o frame_tenths_c, intentar extraer thermal_frame
        if "thermal" in raw_payload and raw_payload["thermal"].get("frame_tenths_c"):
            t = raw_payload["thermal"]
            tf = {
                "type": "thermal_frame",
                "schema_version": 1,
                "device_id": raw_payload.get("device_id", "L419-ESP32-01"),
                "sequence": raw_payload.get("sequence", 0),
                "width": 32,
                "height": 24,
                "ambient_dC": round(raw_payload.get("environment", {}).get("temperature_c", 25.0) * 10),
                "min_dC": round(t.get("min_temp_c", 20.0) * 10),
                "max_dC": round(t.get("max_temp_c", 35.0) * 10),
                "pixels_dC": t["frame_tenths_c"]
            }
            await publish_thermal_frame(tf)
        return

    received_at = datetime.now(timezone.utc).isoformat()
    current_list = evaluate_events(telemetry)
    current_events = {event["code"]: event for event in current_list}

    for code, event in current_events.items():
        if code not in previous_active_events:
            event_log.appendleft({**event, "status": "ACTIVE"})

    for code, old_event in previous_active_events.items():
        if code not in current_events:
            event_log.appendleft({
                **old_event,
                "status": "RESOLVED",
                "timestamp": received_at,
                "description": "La condición dejó de superar el umbral configurado."
            })

    previous_active_events = current_events
    source_error = None

    env = telemetry["environment"]
    air = telemetry["air_quality"]
    acoustic = telemetry["acoustic"]
    light = telemetry["illumination"]
    occupancy = telemetry["occupancy"]
    thermal = telemetry["thermal"]

    last_sequence = telemetry.get("sequence", last_sequence)

    history.append({
        "received_at": received_at,
        "time": datetime.now().astimezone().strftime("%H:%M:%S"),
        "temperature_c": env.get("temperature_c"),
        "co2_ppm": air.get("co2_ppm"),
        "noise_db": acoustic.get("sound_level_db"),
        "illuminance_lux": light.get("illuminance_lux"),
        "estimated_people": occupancy.get("estimated_people")
    })

    latest_bundle = {
        "telemetry": telemetry,
        "received_at": received_at,
        "source": DATA_SOURCE,
        "is_simulated": DATA_SOURCE == "simulator",
        "active_events": list(current_events.values()),
        "event_log": list(event_log)
    }
    await manager.broadcast(latest_bundle)

    # Extraer y propagar thermal_frame si está disponible
    if thermal.get("frame_tenths_c"):
        tf = {
            "type": "thermal_frame",
            "schema_version": 1,
            "device_id": telemetry.get("device_id", "L419-ESP32-01"),
            "sequence": telemetry.get("sequence", 0),
            "width": 32,
            "height": 24,
            "ambient_dC": round(env.get("temperature_c", 25.0) * 10),
            "min_dC": round(thermal.get("min_temp_c", 20.0) * 10),
            "max_dC": round(thermal.get("max_temp_c", 35.0) * 10),
            "pixels_dC": thermal["frame_tenths_c"]
        }
        await publish_thermal_frame(tf)


async def simulator_loop():
    global serial_connected, serial_message
    sequence = 0
    started_at = time.monotonic()
    serial_connected = True
    serial_message = "Receiving simulated thermal frames (~2 FPS)"

    while True:
        sequence += 1
        tf = make_thermal_frame(sequence, started_at)
        await publish_thermal_frame(tf)

        # También actualizamos la telemetría multisensor para compatibilidad
        if sequence % 2 == 0:
            await publish_payload(make_telemetry(sequence // 2, started_at))

        # ~2 FPS (aprox 500 ms)
        await asyncio.sleep(0.5)


async def serial_loop():
    global source_error, serial_connected, serial_message
    while True:
        connection = None
        try:
            connection = await asyncio.to_thread(open_serial, SERIAL_PORT, SERIAL_BAUD)
            serial_connected = True
            serial_message = f"Receiving thermal frames from {SERIAL_PORT} @ {SERIAL_BAUD}"
            print(f"[SERIAL] Conectado a {SERIAL_PORT} @ {SERIAL_BAUD}")
            while True:
                raw = await asyncio.to_thread(read_json_line, connection)
                if raw is None:
                    continue
                try:
                    await publish_payload(raw)
                except Exception as exc:
                    print(f"[SERIAL] Mensaje rechazado: {exc}")
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            serial_connected = False
            source_error = str(exc)
            serial_message = f"Error: {source_error}"
            print(f"[SERIAL] {source_error}. Reintentando en 3 segundos...")
            await asyncio.sleep(3)
        finally:
            if connection is not None:
                try:
                    connection.close()
                except Exception:
                    pass


async def run_data_source():
    if DATA_SOURCE == "serial":
        await serial_loop()
    else:
        await simulator_loop()


@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(run_data_source())
    yield
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass


app = FastAPI(
    title="Smart Classroom L-419 API",
    version="1.0.0",
    description="API de telemetría y eventos del Smart Classroom Digital Twin (Contrato v1.0).",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


@app.get("/api/health")
async def health():
    """Contrato v1.0 Sección 3: Disponibilidad del servidor y del sensor."""
    return {
        "ok": True,
        "serial": {
            "connected": serial_connected,
            "port": SERIAL_PORT,
            "baud_rate": SERIAL_BAUD,
            "message": serial_message,
            "last_sequence": last_sequence
        },
        "has_frame": latest_thermal_frame is not None,
        "last_sequence": last_sequence,
        # Campos heredados para retrocompatibilidad
        "status": "ok",
        "source": DATA_SOURCE,
        "source_error": source_error,
        "thresholds": THRESHOLDS
    }


@app.get("/api/latest")
async def get_latest():
    """Contrato v1.0 Sección 3: Último fotograma térmico recibido."""
    if latest_thermal_frame is None:
        frame_data = None
    else:
        frame_data = latest_thermal_frame

    return {
        "serial": {
            "connected": serial_connected,
            "port": SERIAL_PORT,
            "baud_rate": SERIAL_BAUD
        },
        "frame": frame_data,
        # Datos heredados para retrocompatibilidad
        "telemetry": latest_bundle.get("telemetry") if latest_bundle else None,
        "active_events": latest_bundle.get("active_events", []) if latest_bundle else [],
        "event_log": list(event_log)
    }


@app.get("/api/history")
async def get_history():
    return list(history)


@app.get("/api/events")
async def get_events():
    return list(event_log)


@app.websocket("/ws/thermal")
async def thermal_socket(websocket: WebSocket):
    """Contrato v1.0 Sección 4: Transmisión térmica en tiempo real."""
    await thermal_manager.connect(websocket)
    # 1. El cliente recibe inmediatamente el último fotograma disponible si existe
    if latest_thermal_frame is not None:
        await websocket.send_json(latest_thermal_frame)
    try:
        while True:
            # Mantener conexión activa
            await websocket.receive_text()
    except WebSocketDisconnect:
        thermal_manager.disconnect(websocket)


@app.websocket("/ws/telemetry")
async def telemetry_socket(websocket: WebSocket):
    """Canal WebSocket heredado para telemetría ambiental completa."""
    await manager.connect(websocket)
    if latest_bundle is not None:
        await websocket.send_json(latest_bundle)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
