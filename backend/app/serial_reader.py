import json


def open_serial(port: str, baud_rate: int):
    import serial
    return serial.Serial(port=port, baudrate=baud_rate, timeout=1)


def read_json_line(serial_connection):
    """Lee una línea NDJSON; ignora líneas vacías o JSON inválido."""
    raw = serial_connection.readline()
    if not raw:
        return None
    line = raw.decode("utf-8", errors="replace").strip()
    if not line:
        return None
    try:
        return json.loads(line)
    except json.JSONDecodeError:
        return None
