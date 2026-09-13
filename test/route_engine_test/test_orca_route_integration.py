import pytest

from services.marine_data_sources import get_pfz_candidates
from ai.engines.route_engine.zone_repository import get_route_zones
from ai.engines.route_engine.engine import RouteEngine
from ai.engines.route_engine.schemas import (
    RouteRequest,
    Coordinate,
    RouteDestination,
    RouteConstraints,
)
from ai.engines.route_engine.route_node import route_node
from services.risk_engine_service.weather_batch import get_weather_data_batch
from services.risk_engine_service.marine_batch import get_marine_batch
from ai.tools.risk_helper import process_grid


# ---------------------------------------------------------
# REAL TEST DATA
# ---------------------------------------------------------

START = {
    "latitude": 13.0827,
    "longitude": 80.2707,
}

TIME = "2026-09-08T06:00:00"


def fetch_pfz_candidates(latitude: float, longitude: float, radius_km: float = 50):
    result = get_pfz_candidates(
        latitude=latitude,
        longitude=longitude,
        radius_km=radius_km,
    )
    if not isinstance(result, dict):
        return []
    pfz_zones = result.get("pfz_zones", {})
    if isinstance(pfz_zones, dict):
        candidates = list(pfz_zones.values())
    elif isinstance(pfz_zones, list):
        candidates = pfz_zones
    else:
        candidates = []
    for c in candidates:
        if "coastal_reference" not in c and "name" in c:
            c["coastal_reference"] = c["name"]
    return candidates


# ---------------------------------------------------------
# 1. TEST REAL PFZ DATA FROM MONGODB
# ---------------------------------------------------------

@pytest.mark.asyncio
async def test_real_pfz_data():

    candidates = fetch_pfz_candidates(
        latitude=START["latitude"],
        longitude=START["longitude"],
        radius_km=50,
    )

    assert candidates is not None
    assert isinstance(candidates, list)

    print("\nPFZ candidates found:", len(candidates))

    if not candidates:
        pytest.skip("No PFZ available in MongoDB for this location")

    pfz = candidates[0]

    assert "latitude" in pfz
    assert "longitude" in pfz

    assert -90 <= float(pfz["latitude"]) <= 90
    assert -180 <= float(pfz["longitude"]) <= 180

    print("Selected PFZ:", pfz)


# ---------------------------------------------------------
# 2. TEST REAL MARINE ZONES FROM MONGODB
# ---------------------------------------------------------

@pytest.mark.asyncio
async def test_real_marine_zones():

    zones = await get_route_zones()

    assert zones is not None
    assert "restricted" in zones
    assert "protected" in zones

    assert isinstance(zones["restricted"], list)
    assert isinstance(zones["protected"], list)

    print(
        "\nRestricted zones:",
        len(zones["restricted"])
    )

    print(
        "Protected zones:",
        len(zones["protected"])
    )


# ---------------------------------------------------------
# 3. TEST ROUTE ENGINE WITH REAL PFZ + ZONES
# ---------------------------------------------------------

@pytest.mark.asyncio
async def test_real_route_generation():

    pfz_candidates = fetch_pfz_candidates(
        latitude=START["latitude"],
        longitude=START["longitude"],
        radius_km=50,
    )

    if not pfz_candidates:
        pytest.skip("No real PFZ data available")

    pfz = pfz_candidates[0]

    zones = await get_route_zones()

    request = RouteRequest(
        start=Coordinate(
            latitude=START["latitude"],
            longitude=START["longitude"],
        ),
        destination=RouteDestination(
            coastal_reference=pfz["coastal_reference"],
            latitude=pfz["latitude"],
            longitude=pfz["longitude"],
        ),
        time=TIME,
        constraints=RouteConstraints(
            avoid_restricted_zones=True,
            restricted_zones=zones["restricted"],
        ),
    )

    engine = RouteEngine()

    result = engine.generate_routes(
        request,
        max_routes=3,
    )

    assert result is not None
    assert result.routes

    assert len(result.routes) <= 3

    print("\nRoutes generated:", len(result.routes))

    for route in result.routes:

        assert route.distance_km > 0
        assert route.waypoints

        print(
            route.route_id,
            "distance:",
            route.distance_km,
            "waypoints:",
            len(route.waypoints),
        )


# ---------------------------------------------------------
# 4. TEST REAL WEATHER DATA
# ---------------------------------------------------------

@pytest.mark.asyncio
async def test_real_weather_data():

    pfz_candidates = fetch_pfz_candidates(
        latitude=START["latitude"],
        longitude=START["longitude"],
        radius_km=50,
    )

    if not pfz_candidates:
        pytest.skip("No PFZ available")

    pfz = pfz_candidates[0]

    nodes = [
        {
            "node_id": "test_node_1",
            "latitude": START["latitude"],
            "longitude": START["longitude"],
        },
        {
            "node_id": "test_node_2",
            "latitude": pfz["latitude"],
            "longitude": pfz["longitude"],
        },
    ]

    weather = await get_weather_data_batch(
        nodes,
        TIME,
    )

    assert weather is not None
    assert isinstance(weather, dict)

    assert "test_node_1" in weather
    assert "test_node_2" in weather

    print("\nWeather data:")
    print(weather)


# ---------------------------------------------------------
# 5. TEST REAL MARINE DATA
# ---------------------------------------------------------

@pytest.mark.asyncio
async def test_real_marine_data():

    pfz_candidates = fetch_pfz_candidates(
        latitude=START["latitude"],
        longitude=START["longitude"],
        radius_km=50,
    )

    if not pfz_candidates:
        pytest.skip("No PFZ available")

    pfz = pfz_candidates[0]

    nodes = [
        {
            "node_id": "test_node_1",
            "latitude": START["latitude"],
            "longitude": START["longitude"],
        },
        {
            "node_id": "test_node_2",
            "latitude": pfz["latitude"],
            "longitude": pfz["longitude"],
        },
    ]

    marine = await get_marine_batch(
        nodes,
        TIME,
    )

    assert marine is not None
    assert isinstance(marine, dict)

    assert "test_node_1" in marine
    assert "test_node_2" in marine

    print("\nMarine data:")
    print(marine)


# ---------------------------------------------------------
# 6. TEST RISK HELPER WITH REAL DATA
# ---------------------------------------------------------

@pytest.mark.asyncio
async def test_real_risk_helper():

    pfz_candidates = fetch_pfz_candidates(
        latitude=START["latitude"],
        longitude=START["longitude"],
        radius_km=50,
    )

    if not pfz_candidates:
        pytest.skip("No PFZ available")

    pfz = pfz_candidates[0]

    nodes = [
        {
            "node_id": "test_node_1",
            "latitude": START["latitude"],
            "longitude": START["longitude"],
        },
        {
            "node_id": "test_node_2",
            "latitude": pfz["latitude"],
            "longitude": pfz["longitude"],
        },
    ]

    k7_input = {
        "nodes": nodes,
        "time": TIME,
    }

    results = await process_grid(k7_input)

    assert results
    assert isinstance(results, list)

    for result in results:

        assert "node_id" in result
        assert "risk_score" in result
        assert "safe" in result

        assert isinstance(result["risk_score"], (int, float))
        assert 0 <= result["risk_score"] <= 100

        assert isinstance(result["safe"], bool)

        print(
            result["node_id"],
            "risk:",
            result["risk_score"],
            "safe:",
            result["safe"],
        )


# ---------------------------------------------------------
# 7. FULL ROUTE NODE INTEGRATION TEST
# ---------------------------------------------------------

@pytest.mark.asyncio
async def test_full_route_node_real_data():

    pfz_candidates = fetch_pfz_candidates(
        latitude=START["latitude"],
        longitude=START["longitude"],
        radius_km=50,
    )

    if not pfz_candidates:
        pytest.skip("No PFZ available")

    pfz = pfz_candidates[0]

    state = {
        "location": {
            "latitude": START["latitude"],
            "longitude": START["longitude"],
        },

        "time_context": {
            "specific_time": TIME,
        },

        "selected_pfz": {
            "coastal_reference": pfz["coastal_reference"],
            "latitude": pfz["latitude"],
            "longitude": pfz["longitude"],
        },

        "route_required": True,

        "workflow_status": "routing",
    }

    result = await route_node(state)

    assert result is not None

    assert "route_result" in result
    assert "risk_result" in result
    assert "workflow_status" in result

    route_result = result["route_result"]
    risk_result = result["risk_result"]

    assert "candidate_routes" in route_result
    assert "safe_route" in route_result

    assert isinstance(
        route_result["candidate_routes"],
        list,
    )

    assert len(
        route_result["candidate_routes"]
    ) <= 3

    assert "routes" in risk_result
    assert "selected_route_id" in risk_result
    assert "safe_route_found" in risk_result

    print("\n========== FULL ORCA ROUTE TEST ==========")

    print(
        "Candidate routes:",
        len(route_result["candidate_routes"])
    )

    print(
        "Safe route:",
        route_result["safe_route"]
    )

    print(
        "Selected route ID:",
        risk_result["selected_route_id"]
    )

    print(
        "Safe route found:",
        risk_result["safe_route_found"]
    )

    print(
        "Workflow:",
        result["workflow_status"]
    )


# ---------------------------------------------------------
# 8. VERIFY BEST SAFE ROUTE IS ACTUALLY LOWEST RISK
# ---------------------------------------------------------

@pytest.mark.asyncio
async def test_safest_route_selection():

    pfz_candidates = fetch_pfz_candidates(
        latitude=START["latitude"],
        longitude=START["longitude"],
        radius_km=50,
    )

    if not pfz_candidates:
        pytest.skip("No PFZ available")

    pfz = pfz_candidates[0]

    state = {
        "location": {
            "latitude": START["latitude"],
            "longitude": START["longitude"],
        },

        "time_context": {
            "specific_time": TIME,
        },

        "selected_pfz": {
            "coastal_reference": pfz["coastal_reference"],
            "latitude": pfz["latitude"],
            "longitude": pfz["longitude"],
        },

        "route_required": True,
        "workflow_status": "routing",
    }

    result = await route_node(state)

    risk_result = result["risk_result"]

    routes = risk_result["routes"]

    if not risk_result["safe_route_found"]:
        pytest.skip("No safe route found for current real data")

    selected_id = risk_result["selected_route_id"]

    selected = next(
        route
        for route in routes
        if route["route_id"] == selected_id
    )

    safe_routes = [
        route
        for route in routes
        if route["safe"]
    ]

    lowest_risk = min(
        route["risk_score"]
        for route in safe_routes
    )

    assert selected["risk_score"] == lowest_risk

    assert selected["safe"] is True

    print("\nSafest route:")
    print(selected)


# ---------------------------------------------------------
# 9. VERIFY FINAL AgentState STRUCTURE
# ---------------------------------------------------------

@pytest.mark.asyncio
async def test_agent_state_route_result():

    pfz_candidates = fetch_pfz_candidates(
        latitude=START["latitude"],
        longitude=START["longitude"],
        radius_km=50,
    )

    if not pfz_candidates:
        pytest.skip("No PFZ available")

    pfz = pfz_candidates[0]

    state = {
        "location": {
            "latitude": START["latitude"],
            "longitude": START["longitude"],
        },

        "time_context": {
            "specific_time": TIME,
        },

        "selected_pfz": {
            "coastal_reference": pfz["coastal_reference"],
            "latitude": pfz["latitude"],
            "longitude": pfz["longitude"],
        },

        "route_required": True,
        "workflow_status": "routing",
    }

    result = await route_node(state)

    route_result = result["route_result"]

    assert route_result["coastal_reference"] == (
        pfz["coastal_reference"]
    )

    assert "candidate_routes" in route_result
    assert "safe_route" in route_result
    assert "zones" in route_result

    assert "restricted" in route_result["zones"]
    assert "protected" in route_result["zones"]

    print("\nAgentState.route_result:")
    print(route_result)