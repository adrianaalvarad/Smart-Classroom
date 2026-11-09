import {
  Thermometer,
  Flame,
  Snowflake,
  Cpu,
  Layers,
  Gauge,
  Wifi,
  CheckCircle2,
  AlertCircle
} from "lucide-react";

export function Dashboard({
  serialStatus,
  ambientTempC,
  minTempC,
  maxTempC,
  sequence,
  frameCount,
  fps,
  serverOk,
  wsStatus
}) {
  const isSerialConnected = Boolean(serialStatus?.connected);
  const isBackendConnected = wsStatus === "connected" && serverOk;

  return (
    <section className="dashboard-grid">
      {/* 1. Estado de Conexión del Sensor */}
      <article className="stat-card">
        <div className="stat-card-header">
          <span className="stat-card-title">Sensor ESP32 / USB Serial</span>
          <span className={`status-indicator ${isSerialConnected ? "online" : "offline"}`}>
            <Cpu size={18} />
          </span>
        </div>
        <div className="stat-card-body">
          <div className="stat-main-row">
            <span className="stat-value-badge">
              {isSerialConnected ? (
                <span className="text-success"><CheckCircle2 size={16} /> Conectado</span>
              ) : (
                <span className="text-danger"><AlertCircle size={16} /> Desconectado</span>
              )}
            </span>
          </div>
          <div className="stat-meta">
            <span><strong>Puerto:</strong> {serialStatus?.port || "—"}</span>
            <span><strong>Bauds:</strong> {serialStatus?.baud_rate || 460800}</span>
          </div>
          <div className="stat-subdetail" title={serialStatus?.message}>
            {serialStatus?.message || "Sin telemetría"}
          </div>
        </div>
      </article>

      {/* 2. Temperatura Ambiente */}
      <article className="stat-card">
        <div className="stat-card-header">
          <span className="stat-card-title">Temperatura Ambiente</span>
          <span className="status-indicator temp-ambient">
            <Thermometer size={18} />
          </span>
        </div>
        <div className="stat-card-body">
          <div className="stat-main-value">
            {ambientTempC !== null ? ambientTempC : "—"}
            <span className="stat-unit">°C</span>
          </div>
          <div className="stat-subdetail">
            Lectura base de referencia del aula L-419
          </div>
        </div>
      </article>

      {/* 3. Temperaturas Extrema: Mínima y Máxima */}
      <article className="stat-card">
        <div className="stat-card-header">
          <span className="stat-card-title">Rango Térmico Matriz</span>
          <span className="status-indicator temp-range">
            <Flame size={18} />
          </span>
        </div>
        <div className="stat-card-body">
          <div className="dual-stat-row">
            <div className="dual-stat-item min">
              <span className="dual-stat-label"><Snowflake size={13} /> Mínima</span>
              <span className="dual-stat-val">
                {minTempC !== null ? minTempC : "—"} <small>°C</small>
              </span>
            </div>
            <div className="stat-divider" />
            <div className="dual-stat-item max">
              <span className="dual-stat-label"><Flame size={13} /> Máxima</span>
              <span className="dual-stat-val">
                {maxTempC !== null ? maxTempC : "—"} <small>°C</small>
              </span>
            </div>
          </div>
          <div className="stat-subdetail">
            Δ Diferencial: {minTempC !== null && maxTempC !== null ? (maxTempC - minTempC).toFixed(1) + " °C" : "—"}
          </div>
        </div>
      </article>

      {/* 4. Fotogramas y Frecuencia Observada (FPS) */}
      <article className="stat-card">
        <div className="stat-card-header">
          <span className="stat-card-title">Telemetría y Frecuencia</span>
          <span className="status-indicator frequency">
            <Gauge size={18} />
          </span>
        </div>
        <div className="stat-card-body">
          <div className="dual-stat-row">
            <div className="dual-stat-item">
              <span className="dual-stat-label"><Layers size={13} /> Fotogramas</span>
              <span className="dual-stat-val">
                {sequence ?? frameCount}
              </span>
            </div>
            <div className="stat-divider" />
            <div className="dual-stat-item">
              <span className="dual-stat-label"><Gauge size={13} /> FPS Observado</span>
              <span className="dual-stat-val highlight-fps">
                {fps > 0 ? `${fps}` : "0.0"} <small>fps</small>
              </span>
            </div>
          </div>
          <div className="stat-subdetail">
            Objetivo nominal: ~2.0 FPS por WebSocket
          </div>
        </div>
      </article>

      {/* 5. Comunicación Backend */}
      <article className="stat-card">
        <div className="stat-card-header">
          <span className="stat-card-title">Enlace con Backend</span>
          <span className="status-indicator comm">
            <Wifi size={18} />
          </span>
        </div>
        <div className="stat-card-body">
          <div className="stat-main-row">
            <span className="stat-value-badge">
              {isBackendConnected ? (
                <span className="text-success"><CheckCircle2 size={16} /> WebSocket Activo</span>
              ) : wsStatus === "connecting" ? (
                <span className="text-warning"><AlertCircle size={16} /> Conectando...</span>
              ) : (
                <span className="text-danger"><AlertCircle size={16} /> Desconectado</span>
              )}
            </span>
          </div>
          <div className="stat-meta">
            <span><strong>REST /health:</strong> {serverOk ? "200 OK" : "Sin respuesta"}</span>
          </div>
          <div className="stat-subdetail">
            Recepción push sin sobrecarga por polling HTTP
          </div>
        </div>
      </article>
    </section>
  );
}
