from pydantic import BaseModel, EmailStr, field_validator, Field


class RegisterRequest(BaseModel):
    username: str = Field(min_length=1)
    email: EmailStr
    password: str = Field(
        min_length=8,
        max_length=128,
        pattern=r"^(?=.*[A-Za-z])(?=.*\d).*$"
    )

class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    role: str
    language: str

    class Config:
        from_attributes = True


class MessageResponse(BaseModel):
    message: str