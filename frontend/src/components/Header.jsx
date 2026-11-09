import { useState } from "react";
import { Activity, Radio, Sparkles, Server, Info, X, Check, RefreshCw } from "lucide-react";

export function Header({
  mode,
  setMode,
  wsStatus,
  serverOk,
  apiBaseUrl,
  wsUrl,
  updateServerIp
}) {
  const [showConfig, setShowConfig] = useState(false);
  const [inputIp, setInputIp] = useState("10.100.101.227");

  const getStatusBadge = () => {
    if (mode === "DEMO") {
      return (
        <span className="badge badge-demo">
          <Sparkles size={14} /> Modo DEMO (Simulación)
        </span>
      );
    }
    if (wsStatus === "connected") {
      return (
        <span className="badge badge-online">
          <span className="pulsing-dot" /> En vivo (WS conectado)
        </span>
      );
    }
    if (wsStatus === "connecting") {
      return (
        <span className="badge badge-warning">
          <Radio size={14} className="spin" /> Conectando a {new URL(wsUrl).hostname}...
        </span>
      );
    }
    return (
      <span className="badge badge-offline">
        <Radio size={14} /> Desconectado ({new URL(wsUrl).hostname})
      </span>
    );
  };

  const handleApplyIp = (ipToApply) => {
    const target = ipToApply || inputIp;
    if (updateServerIp && target.trim()) {
      updateServerIp(target.trim());
    }
  };

  return (
    <header className="app-header">
      <div className="header-brand">
        <div className="brand-logo">
          <Activity size={24} />
        </div>
        <div>
          <div className="brand-title">Smart Classroom Digital Twin</div>
          <div className="brand-subtitle">Aula L-419 · MLX90640 (32 × 24)</div>
        </div>
      </div>

      <div className="header-actions">
        {getStatusBadge()}

        <div className="mode-toggle-group">
          <button
            type="button"
            className={`btn-mode ${mode === "LIVE" ? "active live" : ""}`}
            onClick={() => setMode("LIVE")}
            title="Conectar a FastAPI en vivo vía WebSocket"
          >
            <Radio size={14} /> LIVE
          </button>
          <button
            type="button"
            className={`btn-mode ${mode === "DEMO" ? "active demo" : ""}`}
            onClick={() => setMode("DEMO")}
            title="Ejecutar simulación térmica local autónoma"
          >
            <Sparkles size={14} /> DEMO
          </button>
        </div>

        <button
          type="button"
          className="btn-icon"
          onClick={() => setShowConfig(!showConfig)}
          title="Ver o cambiar dirección IP del servidor"
        >
          <Server size={18} />
        </button>
      </div>

      {showConfig && (
        <div className="config-modal-backdrop" onClick={() => setShowConfig(false)}>
          <div className="config-modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3><Info size={18} /> Configuración del Servidor Backend</h3>
              <button type="button" className="btn-close" onClick={() => setShowConfig(false)}>
                <X size={18} />
              </button>
            </div>
            <div className="modal-body">
              <p className="modal-description">
                Dirección IP donde corre el backend conectado físicamente al ESP32:
              </p>

              {/* Formulario para cambiar IP rápidamente */}
              <div style={{ display: "flex", gap: "8px", marginBottom: "14px" }}>
                <input
                  type="text"
                  value={inputIp}
                  onChange={(e) => setInputIp(e.target.value)}
                  placeholder="ej. 10.100.101.227"
                  style={{
                    flex: 1,
                    padding: "8px 12px",
                    borderRadius: "8px",
                    background: "var(--bg-primary)",
                    border: "1px solid var(--border-subtle)",
                    color: "var(--text-main)",
                    fontSize: "0.86rem"
                  }}
                />
                <button
                  type="button"
                  onClick={() => handleApplyIp(inputIp)}
                  style={{
                    padding: "8px 16px",
                    background: "#0284c7",
                    color: "#fff",
                    border: "none",
                    borderRadius: "8px",
                    fontWeight: "600",
                    cursor: "pointer",
                    fontSize: "0.82rem",
                    display: "flex",
                    alignItems: "center",
                    gap: "6px"
                  }}
                >
                  <RefreshCw size={14} /> Aplicar
                </button>
              </div>

              {/* Botones de acceso rápido */}
              <div style={{ display: "flex", gap: "8px", marginBottom: "16px" }}>
                <button
                  type="button"
                  onClick={() => { setInputIp("10.100.101.227"); handleApplyIp("10.100.101.227"); }}
                  style={{
                    fontSize: "0.75rem",
                    padding: "4px 10px",
                    borderRadius: "6px",
                    background: "rgba(2, 132, 199, 0.15)",
                    color: "#38bdf8",
                    border: "1px solid rgba(2, 132, 199, 0.3)",
                    cursor: "pointer"
                  }}
                >
                  Usar IP 10.100.101.227
                </button>
                <button
                  type="button"
                  onClick={() => { setInputIp("localhost"); handleApplyIp("localhost"); }}
                  style={{
                    fontSize: "0.75rem",
                    padding: "4px 10px",
                    borderRadius: "6px",
                    background: "rgba(255, 255, 255, 0.05)",
                    color: "var(--text-muted)",
                    border: "1px solid var(--border-subtle)",
                    cursor: "pointer"
                  }}
                >
                  Usar localhost
                </button>
              </div>

              <div className="config-row">
                <span className="config-label">API Base URL:</span>
                <code className="config-value">{apiBaseUrl}</code>
              </div>
              <div className="config-row">
                <span className="config-label">WebSocket URL:</span>
                <code className="config-value">{wsUrl}</code>
              </div>
              <div className="config-row">
                <span className="config-label">Estado REST (/api/health):</span>
                <span className={serverOk ? "text-success" : "text-danger"}>
                  {serverOk ? "Disponible (200 OK)" : "No responde (revisar IP o firewall en el backend)"}
                </span>
              </div>
              <div className="config-note">
                <strong>Consejo de conexión:</strong> Asegúrate de que en la máquina con IP <code>10.100.101.227</code> el firewall permita conexiones entrantes en el puerto <code>8000</code> y que Uvicorn esté escuchando en <code>0.0.0.0</code> (no solo 127.0.0.1).
              </div>
            </div>
          </div>
        </div>
      )}
    </header>
  );
}
