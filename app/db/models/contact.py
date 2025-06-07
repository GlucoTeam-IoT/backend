from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.orm import relationship
from app.db.database import Base

class Contact(Base):
    __tablename__ = "contacts"

    id = Column(String(36), primary_key=True, index=True) 
    email = Column(String(255), unique=True, index=True)
    name = Column(String(100), nullable=True)
    phone = Column(String(20), nullable=True)
    user_id = Column(String(36), ForeignKey('users.id'), nullable=False)
    user = relationship("User", back_populates="contacts")