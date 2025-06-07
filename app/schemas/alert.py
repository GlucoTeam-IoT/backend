from datetime import datetime
from pydantic import BaseModel
from enum import Enum

class AlertLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class AlertBase(BaseModel):
    message: str | None = None
    level: AlertLevel
    timestamp: datetime

class AlertCreate(BaseModel):
    device_id: str
    level: AlertLevel | None = None
    message: str | None = None

class Alert(AlertBase):
    id: str
    device_id: str

    class Config:
        from_attributes = True
