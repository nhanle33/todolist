from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime


class UserRegister(BaseModel):
    """Schema for user registration"""
    email: str = Field(..., description="User email")
    password: str = Field(..., min_length=6, max_length=72, description="Password (6-72 chars, bcrypt limit)")


class UserLogin(BaseModel):
    """Schema for user login"""
    email: str = Field(..., description="User email")
    password: str = Field(..., description="Password")


class UserResponse(BaseModel):
    """Schema for user response"""
    id: int
    email: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    """Schema for token response"""
    access_token: str
    token_type: str = "bearer"


class CurrentUser(BaseModel):
    """Schema for current user"""
    id: int
    email: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True
