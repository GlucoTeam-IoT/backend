from pydantic import BaseModel, EmailStr

class ContactBase(BaseModel):
    email: EmailStr

class ContactCreate(ContactBase):
    name: str
    phone: str 

class ContactUpdate(BaseModel):
    email: EmailStr | None = None
    name: str | None = None
    phone: str | None = None

class Contact(ContactBase):
    id: str
    name: str
    phone: str
    user_id: str 
    
    class Config:
        from_attributes = True