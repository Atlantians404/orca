from datetime import datetime

from pydantic import BaseModel, field_validator


class SessionCreate(BaseModel):
    title: str

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Title cannot be empty")

        return value


class SessionUpdate(BaseModel):
    title: str | None = None

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str | None) -> str | None:
        if value is not None:
            value = value.strip()

            if not value:
                raise ValueError("Title cannot be empty")

        return value


class SessionResponse(BaseModel):
    id: int
    title: str
    is_pinned: bool
    is_archived: bool
    updated_at: datetime

    class Config:
        from_attributes = True


class SessionListResponse(BaseModel):
    items: list[SessionResponse]
    page: int
    limit: int
    total: int
    pages: int