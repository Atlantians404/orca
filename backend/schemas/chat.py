from pydantic import BaseModel
from typing import Optional, Any

class ChatRequest(BaseModel):
    session_id: int
    message: str


class ChatResponse(BaseModel):
    message: str

class MessageResponse(BaseModel):
    id: int
    role: str
    content: str
    response_data: Optional[Any] = None

    class Config:
        from_attributes = True