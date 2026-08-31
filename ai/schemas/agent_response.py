from pydantic import BaseModel, Field

class MapData(BaseModel):
    coordinates: list[list[float]] = Field(default_factory=list)

class AgentResponse(BaseModel):
    message: str
    map: MapData | None = None