from pydantic import BaseModel, EmailStr
from uuid import UUID
from typing import Optional

class UserBase(BaseModel):
    email:EmailStr
    name:str
    address:Optional[str]=None
    mobile:Optional[int]

class UserCreate(UserBase):
    password:str
    
class UserResponse(UserBase):
    id:UUID
    class Config:
        form_attributes = True

class UserLogin(BaseModel):
    email:EmailStr
    password:str
    