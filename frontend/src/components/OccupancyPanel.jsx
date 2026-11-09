import { Users, LogIn, LogOut, History, AlertTriangle, ShieldCheck } from "lucide-react";

export function OccupancyPanel() {
  return (
    <section className="occupancy-card">
      <div className="occupancy-header">
        <div>
          <div className="viewer-eyebrow">MÓDULO C · SEGUIMIENTO Y AFORO</div>
          <h2 className="occupancy-title">Estado de Ocupación del Aula L-419</h2>
          <p className="occupancy-subtitle">
            Módulo preparado para recepción de telemetría de flujo de personas.
          </p>
        </div>
      </div>

      {/* AVISO OBLIGATORIO SEGÚN SECCIÓN 6 DEL CONTRATO */}
      <div className="occupancy-disclaimer-box">
        <div className="disclaimer-icon">
          <AlertTriangle size={20} />
        </div>
        <div className="disclaimer-content">
          <strong>Aviso de rigor metodológico (Sección 6 del Contrato):</strong>
          <p>
            Estos eventos todavía <strong>no forman parte del contrato actual del backend</strong> ni representan
            mediciones validadas. No se inventan mediante procesamiento heurístico no calibrado. Se habilitarán formalmente
            cuando se desarrolle y valide el algoritmo de detección y seguimiento de personas sobre la matriz MLX90640.
          </p>
        </div>
      </div>

      {/* Tarjetas de Marcador de Posición (Placeholders) */}
      <div className="occupancy-grid">
        {/* Personas dentro */}
        <div className="occupancy-item placeholder-item">
          <div className="occupancy-item-icon bg-blue">
            <Users size={20} />
          </div>
          <div className="occupancy-item-copy">
            <span className="occupancy-item-label">Personas dentro del aula</span>
            <div className="occupancy-item-value">
              <span className="placeholder-dash">—</span>
              <span className="badge-pending">Pendiente de algoritmo</span>
            </div>
            <span className="occupancy-item-meta">Capacidad de diseño: 30 alumnos</span>
          </div>
        </div>

        {/* Total entradas */}
        <div className="occupancy-item placeholder-item">
          <div className="occupancy-item-icon bg-emerald">
            <LogIn size={20} />
          </div>
          <div className="occupancy-item-copy">
            <span className="occupancy-item-label">Total de entradas</span>
            <div className="occupancy-item-value">
              <span className="placeholder-dash">—</span>
              <span className="badge-pending">Pendiente de algoritmo</span>
            </div>
            <span className="occupancy-item-meta">Conteo acumulado por umbral</span>
          </div>
        </div>

        {/* Total salidas */}
        <div className="occupancy-item placeholder-item">
          <div className="occupancy-item-icon bg-amber">
            <LogOut size={20} />
          </div>
          <div className="occupancy-item-copy">
            <span className="occupancy-item-label">Total de salidas</span>
            <div className="occupancy-item-value">
              <span className="placeholder-dash">—</span>
              <span className="badge-pending">Pendiente de algoritmo</span>
            </div>
            <span className="occupancy-item-meta">Conteo acumulado por umbral</span>
          </div>
        </div>
      </div>

      {/* Historial de movimientos (Placeholder visual preparado) */}
      <div className="occupancy-history-placeholder">
        <div className="history-header">
          <div className="history-title">
            <History size={16} /> Historial de flujo y eventos de tránsito
          </div>
          <span className="history-state-badge">Espacio reservado</span>
        </div>
        <div className="history-empty-state">
          <div className="empty-dots">
            <span /> <span /> <span />
          </div>
          <p>
            El registro cronológico de entradas y salidas se integrará cuando el nodo de visión térmica transmita el flujo verificado.
          </p>
        </div>
      </div>
    </section>
  );
}
