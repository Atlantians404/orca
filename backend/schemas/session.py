from pydantic import BaseModel


class SessionCreate(BaseModel):
    title: str


class SessionUpdate(BaseModel):
    title: str | None = None


class SessionResponse(BaseModel):
    id: int
    title: str
    summary: str | None = None

    class Config:
        from_attributes = True