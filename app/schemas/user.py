from pydantic import BaseModel, EmailStr, validator
from typing import Optional, List
import re

# Base User schema with shared attributes
class UserBase(BaseModel):
    email: EmailStr
    username: str
    is_active: Optional[bool] = True
    is_superuser: Optional[bool] = False
    full_name: Optional[str] = None
    
    @validator('username')
    def username_alphanumeric(cls, v):
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError('Username must be alphanumeric with optional underscores and hyphens')
        return v

# Schema for creating a new user
class UserCreate(UserBase):
    password: str
    
    @validator('password')
    def password_strong_enough(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        return v

# Schema for updating user
class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None
    full_name: Optional[str] = None
    password: Optional[str] = None

# Schema for user output
class User(UserBase):
    id: int
    
    class Config:
        orm_mode = True
        
# Schema for token
class Token(BaseModel):
    access_token: str
    token_type: str

# Schema for token data
class TokenPayload(BaseModel):
    sub: Optional[int] = None 