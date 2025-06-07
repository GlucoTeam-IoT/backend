from sqlalchemy import Column, ForeignKey, String, DateTime, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base
import enum

class Status(enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"

class Device(Base):
    __tablename__ = "devices"

    id = Column(String(36), primary_key=True, index=True)
    status = Column(Enum(Status), nullable=False, default=Status.ACTIVE)
    timestamp = Column(DateTime, default=func.now(), nullable=False)
    
    # Foreign keys
    user_id = Column(String(36), ForeignKey('users.id'), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="devices")
    records = relationship("Record", back_populates="device", 
                         foreign_keys="[Record.device_id]",
                         primaryjoin="Device.id == Record.device_id")
    alerts = relationship("Alert", back_populates="device", cascade="all, delete-orphan")