from pydantic import BaseModel


class Visualization(BaseModel):
    type: str
    x_axis: dict | None = None
    y_axis: dict | None = None
    data: list[dict]


class MapData(BaseModel):
    coordinates: list[list[float]]


class AgentResponse(BaseModel):
    message: str
    visualization: Visualization | None = None
    map: MapData | None = None