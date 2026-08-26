from typing import List, Optional

from pydantic import BaseModel, Field


class RequestInfo(BaseModel):
    request_id: str
    requires_route: bool = False
    forecast_hours: int = Field(default=24, ge=1, le=168)


class MarineData(BaseModel):
    sea_state: str
    current_speed: float = Field(ge=0)
    marine_warning: str


class WeatherData(BaseModel):
    wind_speed: float = Field(ge=0)
    wind_direction: float = Field(ge=0, lt=360)
    wave_height: float = Field(ge=0)
    visibility: float = Field(ge=0)
    precipitation: float = Field(ge=0, le=100)
    lightning: bool
    condition: str


class GeoData(BaseModel):
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    restricted_area: bool = False
    protected_area: bool = False


class RiskInput(BaseModel):
    request: RequestInfo
    marine: MarineData
    weather: WeatherData
    geo: GeoData


class RiskResult(BaseModel):
    request_id: str
    score: float
    level: str
    reasons: List[str]
    recommendation: Optional[str] = None
    route_required: bool