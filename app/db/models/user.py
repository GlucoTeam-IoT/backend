from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import relationship
from app.db.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, index=True) 
    email = Column(String(255), unique=True, index=True)
    hashed_password = Column(String(255))
    name = Column(String(100), nullable=True)
    phone = Column(String(20), nullable=True)
    age = Column(Integer, nullable=True) 
    
    contacts = relationship("Contact", back_populates="user", cascade="all, delete-orphan")
    devices = relationship("Device", back_populates="user", cascade="all, delete-orphan")
    records = relationship("Record", back_populates="user", cascade="all, delete-orphan")