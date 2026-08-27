from dataclasses import dataclass


@dataclass
class Coordinate:
    latitude: float
    longitude: float


@dataclass
class PFZ:
    id: str
    latitude: float
    longitude: float
    depth_m: float | None = None