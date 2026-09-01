from pydantic import BaseModel


class SessionCreate(BaseModel):
    title: str


class SessionResponse(BaseModel):
    id: int
    title: str
    summary: str | None = None

    class Config:
        from_attributes = True