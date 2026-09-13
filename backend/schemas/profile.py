from pydantic import BaseModel


class ProfileUpdate(BaseModel):
    display_name: str | None = None
    language: str | None = None


class ProfileResponse(BaseModel):
    id: int
    user_id: int
    display_name: str
    language: str

    class Config:
        from_attributes = True