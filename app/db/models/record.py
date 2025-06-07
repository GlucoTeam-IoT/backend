from sqlalchemy import Column, ForeignKey, String, Integer, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base

class Record(Base):
    __tablename__ = "records"

    id = Column(String(36), primary_key=True, index=True)
    level = Column(Integer, nullable=False)
    description = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=func.now(), nullable=False)
    
    # Foreign keys
    user_id = Column(String(36), ForeignKey('users.id'), nullable=False)
    device_id = Column(String(36), ForeignKey('devices.id'), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="records")
    device = relationship("Device", back_populates="records",
                        foreign_keys=[device_id],
                        primaryjoin="Record.device_id == Device.id")