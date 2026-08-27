from typing import List, Optional

from pydantic import BaseModel, Field


class RequestInfo(BaseModel):
    request_id: str
    requires_route: bool = False
    forecast_hours: int = Field(default=24, ge=1, le=168)


class SwellData(BaseModel):
    height: float = Field(ge=0)
    period: float = Field(ge=0)
    direction: float = Field(ge=0, lt=360)


class CurrentData(BaseModel):
    velocity: float = Field(ge=0)
    direction: float = Field(ge=0, lt=360)


class MarineData(BaseModel):
    wave_height: float = Field(ge=0)
    wave_period: float = Field(ge=0)
    wave_direction: float = Field(ge=0, lt=360)

    sea_state: str

    swell: SwellData

    current: CurrentData

    marine_warning: str


class WeatherData(BaseModel):
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)

    time: str

    temperature: float

    wind_speed: float = Field(ge=0)
    wind_direction: float = Field(ge=0, lt=360)
    wind_gust: float = Field(ge=0)

    visibility: float = Field(ge=0)
    precipitation: float = Field(ge=0)

    weather_code: int
    weather_condition: str

    thunderstorm: bool


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