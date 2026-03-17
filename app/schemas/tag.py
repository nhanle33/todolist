from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class TagCreate(BaseModel):
    """Schema for creating a tag"""
    name: str = Field(..., min_length=1, max_length=50, description="Tag name (e.g., work, urgent, personal)")
    color: Optional[str] = Field(default="#999999", description="Hex color code (e.g., #FF5733)")


class TagUpdate(BaseModel):
    """Schema for updating a tag"""
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    color: Optional[str] = Field(None)


class TagResponse(BaseModel):
    """Schema for tag response"""
    id: int
    name: str
    color: str
    created_at: datetime

    class Config:
        from_attributes = True
