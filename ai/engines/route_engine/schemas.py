from pydantic import BaseModel, Field


# =========================================================
# COORDINATE
# =========================================================

class Coordinate(BaseModel):
    """
    Geographic coordinate.

    Latitude  : -90 to 90
    Longitude : -180 to 180
    """

    latitude: float = Field(
        ...,
        ge=-90,
        le=90,
    )

    longitude: float = Field(
        ...,
        ge=-180,
        le=180,
    )


# =========================================================
# PFZ
# =========================================================

class PFZ(BaseModel):
    """
    PFZ location obtained from MongoDB.

    coastal_reference is used as the PFZ identifier
    because the PFZ collection does not provide a
    separate PFZ ID.
    """

    coastal_reference: str

    latitude: float = Field(
        ...,
        ge=-90,
        le=90,
    )

    longitude: float = Field(
        ...,
        ge=-180,
        le=180,
    )

    depth_m: float | None = None


# =========================================================
# PROTECTED / RESTRICTED AREA
# =========================================================

class RestrictedZone(BaseModel):
    """
    Marine protected or restricted area.

    This information comes from MongoDB and is used
    by the Route Engine to avoid unsafe zones.
    """

    name: str
    state: str
    type: str
    restriction_level: str

    latitude: float = Field(
        ...,
        ge=-90,
        le=90,
    )

    longitude: float = Field(
        ...,
        ge=-180,
        le=180,
    )

    geometry: dict | None = None


# =========================================================
# ROUTE DESTINATION
# =========================================================

class RouteDestination(BaseModel):
    """
    Destination PFZ for route generation.
    """

    coastal_reference: str

    latitude: float = Field(
        ...,
        ge=-90,
        le=90,
    )

    longitude: float = Field(
        ...,
        ge=-180,
        le=180,
    )


# =========================================================
# ROUTE CONSTRAINTS
# =========================================================

class RouteConstraints(BaseModel):
    """
    Constraints used while generating the route.
    """

    avoid_restricted_zones: bool = True

    restricted_zones: list[RestrictedZone] = Field(
        default_factory=list
    )


# =========================================================
# ROUTE REQUEST
# =========================================================

class RouteRequest(BaseModel):
    """
    Input received by the Route Engine.
    """

    start: Coordinate

    destination: RouteDestination

    # Time context used for route generation
    # and later risk evaluation.
    time: str | None = None

    constraints: RouteConstraints = Field(
        default_factory=RouteConstraints
    )


# =========================================================
# WAYPOINT
# =========================================================

class Waypoint(Coordinate):
    """
    A geographic point belonging to a generated route.
    """

    pass


# =========================================================
# SINGLE ROUTE RESULT
# =========================================================

class RouteResult(BaseModel):
    """
    Represents one candidate route generated
    by the Route Engine.
    """

    route_id: str | None = None

    coastal_reference: str

    start: Coordinate

    destination: Coordinate

    waypoints: list[Waypoint]

    distance_km: float

    geojson: dict


# =========================================================
# MULTIPLE CANDIDATE ROUTES
# =========================================================

class CandidateRoutes(BaseModel):
    """
    Represents multiple candidate routes generated
    by the Route Engine.

    These routes can later be evaluated by
    the Risk Engine.
    """

    coastal_reference: str

    routes: list[RouteResult]