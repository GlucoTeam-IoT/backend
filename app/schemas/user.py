from pydantic import BaseModel, EmailStr

class UserBase(BaseModel):
    email: EmailStr

class UserSignUp(UserBase):
    password: str

class UserSignIn(BaseModel):
    email: EmailStr
    password: str

class UserUpdate(BaseModel):
    email: EmailStr | None = None
    name: str | None = None
    phone: str | None = None
    age: int | None = None

class User(UserBase):
    id: str
    name: str | None = None
    phone: str | None = None
    age: int | None = None
    
    class Config:
        from_attributes = True

