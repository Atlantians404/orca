from pydantic import BaseModel


class Location(BaseModel):
    place: str | None = None
    latitude: float | None = None
    longitude: float | None = None