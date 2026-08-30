from ai.engines.route_engine.engine import RouteEngine

from ai.engines.route_engine.schemas import (
    Coordinate,
    RouteDestination,
    RouteConstraints,
    RouteRequest,
)


def test_complete_route_engine():

    # ============================================
    # 1. USER SOURCE
    # ============================================

    source = Coordinate(
        latitude=12.90,
        longitude=80.30,
    )

    # ============================================
    # 2. SELECTED PFZ
    # ============================================

    selected_pfz = RouteDestination(
        pfz_id="PFZ001",
        latitude=13.00,
        longitude=80.40,
    )

    # ============================================
    # 3. CREATE ROUTE REQUEST
    # ============================================

    request = RouteRequest(
        start=source,
        destination=selected_pfz,
        time="05:00",
        constraints=RouteConstraints(
            avoid_restricted_zones=True,
            restricted_zones=[],
        ),
    )

    # ============================================
    # 4. CALL ROUTE ENGINE
    # ============================================

    result = RouteEngine.find_routes(
        request,
        max_routes=3,
    )

    # ============================================
    # 5. BASIC RESULT VALIDATION
    # ============================================

    assert result.pfz_id == "PFZ001"

    assert len(result.routes) >= 1

    assert len(result.routes) <= 3

    # ============================================
    # 6. DISPLAY RESULT
    # ============================================

    print("\n")
    print("=" * 60)
    print("          ORCA ROUTE ENGINE TEST")
    print("=" * 60)

    print("\nSOURCE")
    print(
        f"Latitude  : {source.latitude}"
    )
    print(
        f"Longitude : {source.longitude}"
    )

    print("\nSELECTED PFZ")
    print(
        f"PFZ ID    : {selected_pfz.pfz_id}"
    )
    print(
        f"Latitude  : {selected_pfz.latitude}"
    )
    print(
        f"Longitude : {selected_pfz.longitude}"
    )

    print("\n")
    print(
        f"Candidate routes generated: "
        f"{len(result.routes)}"
    )

    print("-" * 60)

    # ============================================
    # 7. DISPLAY EVERY ROUTE
    # ============================================

    for route in result.routes:

        print("\n")
        print(
            f"ROUTE: {route.route_id}"
        )

        print(
            f"Distance: "
            f"{route.distance_km:.2f} km"
        )

        print(
            f"Waypoints: "
            f"{len(route.waypoints)}"
        )

        print("\nWaypoint coordinates:")

        for index, waypoint in enumerate(
            route.waypoints,
            start=1,
        ):

            print(
                f"  {index}. "
                f"({waypoint.latitude}, "
                f"{waypoint.longitude})"
            )

        print("\nGeoJSON:")

        print(
            route.geojson
        )

        print("-" * 60)

    # ============================================
    # 8. VERIFY EVERY ROUTE
    # ============================================

    for route in result.routes:

        assert route.route_id is not None

        assert route.pfz_id == "PFZ001"

        assert route.distance_km > 0

        assert len(
            route.waypoints
        ) >= 1

        assert (
            route.geojson["type"]
            == "Feature"
        )

        assert (
            route.geojson["geometry"]["type"]
            == "LineString"
        )

        coordinates = (
            route.geojson["geometry"]["coordinates"]
        )

        assert len(coordinates) >= 2

    print("\n")
    print("=" * 60)
    print("        ROUTE ENGINE TEST PASSED")
    print("=" * 60)