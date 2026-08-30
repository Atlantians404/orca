from pydantic import BaseModel, Field


class TimeSlot(BaseModel):
    date: str
    start_time: str
    end_time: str | None = None


class TimeContext(BaseModel):
    slots: list[TimeSlot] = Field(default_factory=list)
    timezone: str = "Asia/Kolkata"