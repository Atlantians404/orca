from pydantic import BaseModel, field_validator


class ProfileUpdate(BaseModel):
    display_name: str | None = None
    language: str | None = None

    @field_validator("display_name")
    @classmethod
    def validate_display_name(cls, value: str | None) -> str | None:
        if value is not None and not value.strip():
            raise ValueError("Display name cannot be empty")
        return value

    @field_validator("language")
    @classmethod
    def validate_language(cls, value: str | None) -> str | None:
        if value is not None and not value.strip():
            raise ValueError("Language cannot be empty")
        return value


class ProfileResponse(BaseModel):
    id: int
    user_id: int
    display_name: str
    language: str

    class Config:
        from_attributes = True