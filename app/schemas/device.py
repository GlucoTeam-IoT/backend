from pydantic import BaseModel
from datetime import datetime
from enum import Enum

class Status(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"

class DeviceBase(BaseModel):   
    status: Status
    timestamp: datetime

class DeviceCreate(BaseModel):
    timestamp: datetime

class DeviceUpdate(BaseModel):
    timestamp: datetime | None = None
    status: Status | None = None

class Device(DeviceBase):
    id: str
    user_id: str

    class Config:
        from_attributes = True