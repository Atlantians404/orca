from pydantic import BaseModel


class TimeContext(BaseModel):
    date: str | None = None
    start_time: str | None = None
    end_time: str | None = None
    timezone: str = "Asia/Kolkata"