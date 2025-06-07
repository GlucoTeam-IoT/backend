from sqlalchemy import Column, ForeignKey, String, DateTime, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base
import enum

class AlertLevel(enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class Alert(Base):
    __tablename__ = "alerts"

    id = Column(String(36), primary_key=True, index=True) 
    message = Column(String(255), nullable=True)
    level = Column(Enum(AlertLevel), nullable=False)
    timestamp = Column(DateTime, default=func.now(), nullable=False)
    device_id = Column(String(36), ForeignKey('devices.id'), nullable=False)    
    device = relationship("Device", back_populates="alerts")