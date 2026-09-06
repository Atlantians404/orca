from .engine import RouteEngine


def main():

    # =========================================================
    # START LOCATION
    # =========================================================

    chennai = (
        13.0827,
        80.2707
    )

    # =========================================================
    # PFZ DESTINATION
    #
    # PFZ data does not contain a separate ID.
    # coastal_reference is used as the identifier.
    # =========================================================

    pfz = {
        "coastal_reference": "Kathivakkam Chinnakuppam",
        "latitude": 13.494444,
        "longitude": 80.379444,
        "depth_m": 42.0
    }

    # =========================================================
    # CALCULATE DISTANCE
    # =========================================================

    distance = RouteEngine.calculate_distance(
        chennai,
        (
            pfz["latitude"],
            pfz["longitude"]
        )
    )

    # =========================================================
    # DISPLAY RESULT
    # =========================================================

    print(
        f"PFZ: {pfz['coastal_reference']}"
    )

    print(
        f"Latitude: {pfz['latitude']}"
    )

    print(
        f"Longitude: {pfz['longitude']}"
    )

    print(
        f"Depth: {pfz['depth_m']} m"
    )

    print(
        f"Distance: {distance:.2f} km"
    )


if __name__ == "__main__":
    main()