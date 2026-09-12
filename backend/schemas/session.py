from pydantic import BaseModel, field_validator


class SessionCreate(BaseModel):
    title: str

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Title cannot be empty")
        return value


class SessionUpdate(BaseModel):
    title: str | None = None

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str | None) -> str | None:
        if value is not None and not value.strip():
            raise ValueError("Title cannot be empty")
        return value

class SessionResponse(BaseModel):
    id: int
    title: str
    summary: str | None = None

    class Config:
        from_attributes = True


class SessionListResponse(BaseModel):
    items: list[SessionResponse]
    page: int
    limit: int
    total: int
    pages: int