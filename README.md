# Smart Classroom Digital Twin — Aula L-419
## Contrato de Integración Backend – Frontend (v1.0)

**Arquitectura:** React + Vite / Python + FastAPI  
**Dispositivo:** ESP32 DevKit V1 + Cámara Térmica Infrarroja MLX90640 (32 × 24)  
**Canal:** HTTP REST + WebSocket en tiempo real  

---

## 1. Módulos Implementados en el Frontend

* **Módulo A (Dashboard General):**
  * Estado de conexión del sensor USB Serial (`connected`, puerto, baudios, mensaje).
  * Temperatura ambiente ($T_{amb}$ en °C).
  * Rango térmico: Temperatura mínima ($T_{min}$) y máxima ($T_{max}$) en °C.
  * Contador de fotogramas y **FPS observado** en tiempo real.
  * Estado de enlace HTTP REST y WebSocket.

* **Módulo B (Mapa Térmico 32 × 24):**
  * Renderizado acelerado por hardware mediante **HTML5 Canvas** (resolución nativa de 768 píxeles térmicos).
  * Escalas cromáticas térmicas seleccionables: *Ironbow (FLIR)*, *Inferno (perceptualmente uniforme)* y *Rainbow/Jet*.
  * Selector de **Interpolación visual** (suavizado GPU vs píxeles nativos).
  * Marcadores flotantes de punto de máxima ($T_{max}$) y mínima ($T_{min}$) temperatura.
  * Inspección interactiva (*hover*) con mira de coordenadas $(x, y)$ y temperatura en °C.
  * Barra de referencia calibrada en °C.
  * Captura de instantáneas (Snapshot en PNG).

* **Módulo C (Estado de Ocupación):**
  * Espacio visual preparado para personas dentro, total de entradas, total de salidas e historial de tránsito.
  * Aviso metodológico formal indicando que la detección está reservada hasta validar el algoritmo de visión térmica.

---

## 2. Configuración de Entorno (.env)

El archivo `frontend/.env` define las URLs de conexión:

```env
# Ejecución local:
VITE_API_BASE_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000/ws/thermal

# Ejecución remota en red local (sustituir por la IP del backend):
# VITE_API_BASE_URL=http://192.168.1.105:8000
# VITE_WS_URL=ws://192.168.1.105:8000/ws/thermal
```

---

## 3. Ejecución del Frontend

El frontend corre en el puerto **`5174`**:

```powershell
cd frontend
npm install
npm run dev
```

Abrir en el navegador: **[http://localhost:5174](http://localhost:5174)**

### Modos disponibles en la interfaz:
* **LIVE:** Se conecta al WebSocket del backend FastAPI (`ws://.../ws/thermal`).
* **DEMO:** Modo autónomo que genera fotogramas sintéticos a ~2 FPS directamente en el navegador, permitiendo validar la visualización sin necesidad de hardware ni backend.

---

## 4. Ejecución del Backend (FastAPI)

Requisito: Python 3.10 o superior. Corre en el puerto **`8000`**.

### Modo Simulador (por defecto, ~2 FPS):

```powershell
cd backend
py -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Modo ESP32 por USB Serial (460800 baudios):

```powershell
$env:DATA_SOURCE="serial"
$env:SERIAL_PORT="COM6"
$env:SERIAL_BAUD="460800"
uvicorn app.main:app --reload
```

> **Nota:** Cierra Arduino Serial Monitor antes de iniciar FastAPI para evitar conflictos con el puerto COM.

---

## 5. Endpoints de la API

* **GET `/api/health`**: Estado del servidor y del enlace serial con el ESP32.
* **GET `/api/latest`**: Último fotograma térmico recibido (`type: "thermal_frame"`, 768 enteros en `pixels_dC`).
* **WebSocket `ws://localhost:8000/ws/thermal`**: Transmisión continua de cada fotograma térmico a ~2 FPS.
* **Documentación interactiva Swagger**: `http://localhost:8000/docs`

---

## 6. Formato de Datos Térmicos (Contrato v1.0)

* Cada temperatura se transmite en **décimas de grado Celsius** (`_dC`):  
  $$\text{Temperatura (°C)} = \frac{\text{valor\_dC}}{10}$$
* La matriz `pixels_dC` contiene exactamente **768 valores** ordenados por filas (*row-major*):  
  $$\text{Índice} = y \times 32 + x \quad (0 \le x < 32,\; 0 \le y < 24)$$
