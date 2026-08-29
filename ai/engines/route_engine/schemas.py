from pydantic import BaseModel, Field


class Coordinate(BaseModel):
    latitude: float
    longitude: float


class PFZ(BaseModel):
    id: str
    latitude: float
    longitude: float
    depth_m: float | None = None


class RouteDestination(BaseModel):
    pfz_id: str
    latitude: float
    longitude: float


class RouteConstraints(BaseModel):
    avoid_restricted_zones: bool = True

    restricted_zones: list[dict] = Field(
        default_factory=list
    )


class RouteRequest(BaseModel):
    start: Coordinate

    destination: RouteDestination

    time: str | None = None

    constraints: RouteConstraints = Field(
        default_factory=RouteConstraints
    )


class Waypoint(Coordinate):
    pass


class RouteResult(BaseModel):
    pfz_id: str

    start: Coordinate

    destination: Coordinate

    waypoints: list[Waypoint]

    distance_km: float

    geojson: dict