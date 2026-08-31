from typing import Optional

from pydantic import BaseModel, Field


class RequestInfo(BaseModel):

    request_id: str

    requires_route: bool = False

    forecast_hours: int = Field(
        default=24,
        ge=1,
        le=168
    )


class MarineData(BaseModel):

    wave_height: float = Field(ge=0)

    wave_period: float = Field(ge=0)

    wave_direction: float = Field(
        ge=0,
        lt=360
    )

    swell_wave_height: float = Field(ge=0)

    swell_wave_period: float = Field(ge=0)

    swell_wave_direction: float = Field(
        ge=0,
        lt=360
    )

    ocean_current_velocity: float = Field(ge=0)

    ocean_current_direction: float = Field(
        ge=0,
        lt=360
    )

    sea_surface_temperature: float

    sea_level_height_msl: float

    marine_warning: Optional[str] = None


class WeatherData(BaseModel):

    wind_speed: float = Field(ge=0)

    wind_direction: float = Field(
        ge=0,
        lt=360
    )

    wave_height: float = Field(ge=0)

    visibility: float = Field(ge=0)

    precipitation: float = Field(
        ge=0,
        le=100
    )

    lightning: bool

    condition: str


class GeoData(BaseModel):

    latitude: float = Field(
        ge=-90,
        le=90
    )

    longitude: float = Field(
        ge=-180,
        le=180
    )

    restricted_area: bool = False

    protected_area: bool = False


class RiskInput(BaseModel):

    request: RequestInfo

    marine: MarineData

    weather: WeatherData

    geo: GeoData