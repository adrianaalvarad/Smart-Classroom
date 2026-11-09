from pydantic import BaseModel, ConfigDict, Field


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Environment(StrictModel):
    available: bool
    model: str
    temperature_c: float | None = None
    humidity_pct: float | None = Field(default=None, ge=0, le=100)
    pressure_hpa: float | None = None


class AirQuality(StrictModel):
    available: bool
    model: str
    co2_ppm: float | None = Field(default=None, ge=0)


class Acoustic(StrictModel):
    available: bool
    model: str
    rms: float | None = Field(default=None, ge=0)
    sound_level_db: float | None = None


class Illumination(StrictModel):
    available: bool
    model: str
    illuminance_lux: float | None = Field(default=None, ge=0)


class Occupancy(StrictModel):
    available: bool
    model: str
    presence_detected: bool | None = None
    estimated_people: int | None = Field(default=None, ge=0)


class Thermal(StrictModel):
    available: bool
    frame_valid: bool
    width: int = 32
    height: int = 24
    center_temp_c: float | None = None
    mean_temp_c: float | None = None
    min_temp_c: float | None = None
    max_temp_c: float | None = None
    frame_tenths_c: list[int | None] | None = Field(default=None, min_length=768, max_length=768)


class Connectivity(StrictModel):
    wifi_connected: bool
    rssi_dbm: int | None = None


class Telemetry(StrictModel):
    model_config = ConfigDict(extra="forbid")
    schema_version: int = 1
    device_id: str
    sequence: int = Field(ge=0)
    uptime_ms: int = Field(ge=0)
    timestamp_utc: str | None = None
    environment: Environment
    air_quality: AirQuality
    acoustic: Acoustic
    illumination: Illumination
    occupancy: Occupancy
    thermal: Thermal
    connectivity: Connectivity


class ThermalFrame(BaseModel):
    model_config = ConfigDict(extra="ignore")
    type: str = "thermal_frame"
    schema_version: int = 1
    device_id: str = "L419-ESP32-01"
    sequence: int = 0
    width: int = 32
    height: int = 24
    ambient_dC: int
    min_dC: int
    max_dC: int
    pixels_dC: list[int] = Field(..., min_length=768, max_length=768)
