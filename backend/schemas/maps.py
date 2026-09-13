from pydantic import BaseModel


class MapCreate(BaseModel):
    title: str
    route_data: dict


class MapResponse(BaseModel):
    id: int
    user_id: int
    title: str
    route_data: dict

    class Config:
        from_attributes = True