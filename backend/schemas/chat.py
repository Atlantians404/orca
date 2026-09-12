from typing import Any, Optional

from pydantic import BaseModel


class ChatRequest(BaseModel):
    session_id: int
    message: str


class ChatResumeRequest(BaseModel):
    value: Any


class ChatResponse(BaseModel):
    session_id: int
    message: str
    pending_action: Optional[str] = None
    workflow_status: str
    options: Optional[list[Any]] = None


class MessageResponse(BaseModel):
    id: int
    role: str
    content: str
    response_data: Optional[Any] = None

    class Config:
        from_attributes = True