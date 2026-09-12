from pydantic import BaseModel, Field


class Coordinate(BaseModel):
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)


class PFZ(BaseModel):
    coastal_reference: str
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    depth_m: float | None = None


class RestrictedZone(BaseModel):
    name: str
    state: str
    type: str
    restriction_level: str

    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)

    geometry: dict | None = None

    # Backward compatibility with older tests/data
    id: str | None = None
    coordinates: list[list[float]] | None = None


class RouteDestination(Coordinate):
    coastal_reference: str


class RouteConstraints(BaseModel):
    avoid_restricted_zones: bool = True

    restricted_zones: list[RestrictedZone] = Field(
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
    node_id: str | None = None


class RouteResult(BaseModel):
    route_id: str | None = None

    coastal_reference: str

    start: Coordinate
    destination: RouteDestination | Coordinate

    waypoints: list[Waypoint]

    distance_km: float

    geojson: dict


class CandidateRoutes(BaseModel):
    coastal_reference: str

    routes: list[RouteResult]