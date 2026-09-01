from .engine import RouteEngine


def main():

    chennai = (13.0827, 80.2707)

    pfz = (13.1400, 80.4300)

    distance = RouteEngine.calculate_distance(
        chennai,
        pfz
    )

    print(f"Distance: {distance:.2f} km")


if __name__ == "__main__":
    main()