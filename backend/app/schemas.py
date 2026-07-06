from pydantic import BaseModel, HttpUrl
from datetime import datetime
from typing import Optional


class URLCreate(BaseModel):
    url: HttpUrl
    name: Optional[str] = None


class HealthCheckResponse(BaseModel):
    id: int
    status_code: Optional[int]
    response_time_ms: Optional[float]
    is_up: bool
    checked_at: datetime

    class Config:
        from_attributes = True


class URLResponse(BaseModel):
    id: int
    url: str
    name: Optional[str]
    created_at: datetime
    latest_check: Optional[HealthCheckResponse] = None

    class Config:
        from_attributes = True
