from shapely.geometry import shape
from ai.engines.route_engine.engine import RouteEngine
from ai.engines.route_engine.schemas import RouteRequest



from ai.engines.route_engine.geometry import zone_to_polygon
def test_route_around_restricted_zone():

    request = RouteRequest(
        start={
            "latitude": 12.90,
            "longitude": 80.30
        },

        destination={
            "pfz_id": "PFZ07",
            "latitude": 13.00,
            "longitude": 80.40
        },

        time="07:00",

        constraints={
            "avoid_restricted_zones": True,

            "restricted_zones": [
                {
                    "id": "ZONE001",
                    "name": "Marine Restricted Zone",

                    "coordinates": [
                        [12.93, 80.32],
                        [12.93, 80.38],
                        [12.97, 80.38],
                        [12.97, 80.32],
                        [12.93, 80.32]
                    ]
                }
            ]
        }
    )

    result = RouteEngine.find_route(request)

    assert result.pfz_id == "PFZ07"

    assert result.distance_km > 0

    assert len(result.waypoints) >= 1

    assert result.geojson["type"] == "Feature"

    assert (
        result.geojson["geometry"]["type"]
        == "LineString"
    )
    route_geometry = shape(
        result.geojson["geometry"]
    )

    restricted_polygon = zone_to_polygon(
        request.constraints.restricted_zones[0]
    )

    assert not route_geometry.intersects(
        restricted_polygon
    )