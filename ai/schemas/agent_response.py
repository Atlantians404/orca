from typing import Any

from pydantic import BaseModel, Field


class PFZData(BaseModel):
    name: str
    latitude: float
    longitude: float
    distance_from_source_km: float | None = None


class RiskData(BaseModel):
    score: float
    level: str


class WaypointData(BaseModel):
    latitude: float
    longitude: float
    risk_score: float | None = None
    safe: bool | None = None


class RouteData(BaseModel):
    route_id: str
    distance_km: float
    risk_score: float
    safe: bool
    waypoints: list[WaypointData] = Field(default_factory=list)
    geojson: dict[str, Any] | None = None


class MapData(BaseModel):
    coordinates: list[list[float]] = Field(default_factory=list)


class AgentResponse(BaseModel):
    message: str
    map: MapData | None = None
    pfz: PFZData | None = None
    risk: RiskData | None = None
    route: RouteData | None = None