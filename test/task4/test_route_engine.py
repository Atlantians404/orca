from ai.engines.route_engine import RouteEngine


def test_valid_coordinates():

    assert RouteEngine.validate_coordinates(
        13.0827,
        80.2707
    ) is True


def test_invalid_latitude():

    assert RouteEngine.validate_coordinates(
        100,
        80
    ) is False


def test_invalid_longitude():

    assert RouteEngine.validate_coordinates(
        13,
        200
    ) is False


def test_boundary_coordinates():

    assert RouteEngine.validate_coordinates(
        90,
        180
    ) is True