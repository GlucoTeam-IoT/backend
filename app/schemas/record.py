from pydantic import BaseModel
from datetime import datetime

class RecordBase(BaseModel):   
    level: int

class RecordCreate(BaseModel):
    description: str | None = None
    timestamp: datetime | None = None
    device_id: str | None = None
    level: int

class Record(RecordBase):
    id: str
    user_id: str
    device_id: str | None = None
    description: str | None = None
    timestamp: datetime

    class Config:
        from_attributes = True