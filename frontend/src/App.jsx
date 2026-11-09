import { useThermalStream } from "./hooks/useThermalStream";
import { Header } from "./components/Header";
import { Dashboard } from "./components/Dashboard";
import { ThermalViewer } from "./components/ThermalViewer";
import { OccupancyPanel } from "./components/OccupancyPanel";

export default function App() {
  const {
    mode,
    setMode,
    frame,
    fps,
    frameCount,
    wsStatus,
    serialStatus,
    serverOk,
    ambientTempC,
    minTempC,
    maxTempC,
    minPoint,
    maxPoint,
    apiBaseUrl,
    wsUrl,
    updateServerIp
  } = useThermalStream();

  return (
    <div className="app-layout">
      <Header
        mode={mode}
        setMode={setMode}
        wsStatus={wsStatus}
        serverOk={serverOk}
        apiBaseUrl={apiBaseUrl}
        wsUrl={wsUrl}
        updateServerIp={updateServerIp}
      />

      <main className="app-main">
        {/* MÓDULO A: Dashboard General */}
        <Dashboard
          serialStatus={serialStatus}
          ambientTempC={ambientTempC}
          minTempC={minTempC}
          maxTempC={maxTempC}
          sequence={frame?.sequence}
          frameCount={frameCount}
          fps={fps}
          serverOk={serverOk}
          wsStatus={wsStatus}
        />

        {/* CONTENIDO PRINCIPAL: MÓDULO B (Mapa Térmico) y MÓDULO C (Ocupación) */}
        <div className="main-content-grid">
          <div className="thermal-column">
            <ThermalViewer
              frame={frame}
              minTempC={minTempC}
              maxTempC={maxTempC}
              ambientTempC={ambientTempC}
              minPoint={minPoint}
              maxPoint={maxPoint}
            />
          </div>

          <div className="occupancy-column">
            <OccupancyPanel />
          </div>
        </div>
      </main>

      <footer className="app-footer">
        <p>
          Smart Classroom Digital Twin — Aula L-419 · Contrato v1.0 (ESP32 + MLX90640) · UTEC Proyectos de Ingeniería
        </p>
      </footer>
    </div>
  );
}
