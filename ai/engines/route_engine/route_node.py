from typing import Any

from ai.agent_state import AgentState

from .engine import RouteEngine
from .schemas import (
    Coordinate,
    RouteDestination,
    RouteConstraints,
    RouteRequest,
    RestrictedZone,
)

from services.location.marine_zones import (
    restricted_collection,
    protected_collection,
)


# =========================================================
# HELPERS
# =========================================================

async def get_marine_zones() -> list[dict[str, Any]]:
    """
    Fetch restricted and protected marine zones
    from MongoDB.

    Both collections are stored inside:

        ORCA.protected_zones
        ORCA.restricted_zones
    """

    zones = []

    # -----------------------------------------------------
    # RESTRICTED ZONES
    # -----------------------------------------------------

    async for zone in restricted_collection.find({}):

        zones.append(
            {
                "name": zone.get(
                    "name",
                    "Unknown Restricted Zone",
                ),
                "state": zone.get(
                    "state",
                    "",
                ),
                "type": zone.get(
                    "type",
                    "MARINE_RESTRICTED_AREA",
                ),
                "restriction_level": zone.get(
                    "restriction_level",
                    "RESTRICTED",
                ),
                "latitude": zone.get(
                    "latitude",
                    0.0,
                ),
                "longitude": zone.get(
                    "longitude",
                    0.0,
                ),
                "geometry": zone.get(
                    "geometry"
                ),
            }
        )

    # -----------------------------------------------------
    # PROTECTED ZONES
    # -----------------------------------------------------

    async for zone in protected_collection.find({}):

        zones.append(
            {
                "name": zone.get(
                    "name",
                    "Unknown Protected Zone",
                ),
                "state": zone.get(
                    "state",
                    "",
                ),
                "type": zone.get(
                    "type",
                    "MARINE_PROTECTED_AREA",
                ),
                "restriction_level": zone.get(
                    "restriction_level",
                    "PROTECTED",
                ),
                "latitude": zone.get(
                    "latitude",
                    0.0,
                ),
                "longitude": zone.get(
                    "longitude",
                    0.0,
                ),
                "geometry": zone.get(
                    "geometry"
                ),
            }
        )

    return zones


# =========================================================
# BUILD ROUTE ZONES
# =========================================================

def build_route_zones(
    zones: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """
    Convert MongoDB zone documents into the coordinate
    format expected by the Route Engine.

    The geometry is kept because the Route Engine needs
    the actual boundary to avoid the zone.
    """

    route_zones = []

    for zone in zones:

        geometry = zone.get("geometry")

        # -------------------------------------------------
        # Skip zones without usable geometry
        # -------------------------------------------------

        if not geometry:
            continue

        route_zones.append(
            {
                "name": zone.get(
                    "name",
                    "Unknown Zone",
                ),
                "state": zone.get(
                    "state",
                    "",
                ),
                "type": zone.get(
                    "type",
                    "MARINE_ZONE",
                ),
                "restriction_level": zone.get(
                    "restriction_level",
                    "RESTRICTED",
                ),
                "latitude": zone.get(
                    "latitude",
                    0.0,
                ),
                "longitude": zone.get(
                    "longitude",
                    0.0,
                ),
                "geometry": geometry,
            }
        )

    return route_zones


# =========================================================
# EXTRACT TIME
# =========================================================

def get_route_time(
    state: AgentState,
) -> str:
    """
    Extract the first requested time slot from AgentState.
    """

    time_context = state.get(
        "time_context"
    )

    if (
        time_context is None
        or not time_context.slots
    ):
        raise ValueError(
            "Route Engine requires a time context"
        )

    slot = time_context.slots[0]

    requested_time = slot.date

    if slot.start_time:
        requested_time += (
            f"T{slot.start_time}:00"
        )

    return requested_time


# =========================================================
# ROUTE ENGINE NODE
# =========================================================

async def route_engine_node(
    state: AgentState,
) -> dict:
    """
    Route Engine LangGraph node.

    Reads from AgentState:

        location
        selected_pfz
        time_context

    Reads marine zones from MongoDB:

        protected_zones
        restricted_zones

    Sends the complete RouteRequest to RouteEngine.

    Stores the generated routes in:

        route_result
    """

    # =====================================================
    # 1. GET USER LOCATION
    # =====================================================

    location = state.get(
        "location"
    )

    if location is None:

        return {
            "pending_action": "GET_LOCATION",
            "workflow_status": "WAITING_FOR_USER",
        }

    if (
        location.latitude is None
        or location.longitude is None
    ):

        return {
            "pending_action": "GET_LOCATION",
            "workflow_status": "WAITING_FOR_USER",
        }

    # =====================================================
    # 2. GET SELECTED PFZ
    # =====================================================

    selected_pfz = state.get(
        "selected_pfz"
    )

    if selected_pfz is None:

        return {
            "pending_action": "SELECT_PFZ",
            "workflow_status": "WAITING_FOR_USER",
        }

    # =====================================================
    # 3. VALIDATE PFZ COORDINATES
    # =====================================================

    if (
        selected_pfz.get("latitude") is None
        or selected_pfz.get("longitude") is None
    ):

        raise ValueError(
            "Selected PFZ does not contain valid coordinates"
        )

    coastal_reference = selected_pfz.get(
        "coastal_reference"
    )

    if not coastal_reference:

        raise ValueError(
            "Selected PFZ does not contain coastal_reference"
        )

    # =====================================================
    # 4. GET TIME
    # =====================================================

    requested_time = get_route_time(
        state
    )

    # =====================================================
    # 5. CREATE START COORDINATE
    # =====================================================

    start = Coordinate(
        latitude=location.latitude,
        longitude=location.longitude,
    )

    # =====================================================
    # 6. CREATE PFZ DESTINATION
    # =====================================================

    destination = RouteDestination(
        coastal_reference=coastal_reference,
        latitude=selected_pfz["latitude"],
        longitude=selected_pfz["longitude"],
    )

    # =====================================================
    # 7. GET MONGODB MARINE ZONES
    # =====================================================

    zones = await get_marine_zones()

    route_zones = build_route_zones(
        zones
    )

    # =====================================================
    # 8. BUILD ROUTE CONSTRAINTS
    # =====================================================

    restricted_zones = []

    for zone in route_zones:

        # -------------------------------------------------
        # The current Route Engine schema uses
        # RestrictedZone for both protected and restricted
        # marine areas.
        # -------------------------------------------------

        restricted_zones.append(
            RestrictedZone(
                name=zone["name"],
                state=zone["state"],
                type=zone["type"],
                restriction_level=zone["restriction_level"],
                latitude=zone["latitude"],
                longitude=zone["longitude"],
                geometry=zone["geometry"],
            )
        )

    constraints = RouteConstraints(
        avoid_restricted_zones=True,
        restricted_zones=restricted_zones,
    )

    # =====================================================
    # 9. CREATE ROUTE REQUEST
    # =====================================================

    request = RouteRequest(
        start=start,
        destination=destination,
        constraints=constraints,
    )

    # =====================================================
    # 10. RUN ROUTE ENGINE
    # =====================================================

    engine = RouteEngine()

    result = engine.generate_routes(
        request=request,
        time=requested_time,
        max_routes=3,
    )

    # =====================================================
    # 11. STORE RESULT IN AGENT STATE
    # =====================================================

    return {
        "route_required": True,

        "route_result": result.model_dump(),

        "pending_action": None,

        "workflow_status": "IN_PROGRESS",
    }