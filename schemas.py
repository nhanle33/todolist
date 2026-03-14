from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class ToDoCreate(BaseModel):
    """Schema for creating a new todo"""
    title: str = Field(..., min_length=3, max_length=100)
    is_done: bool = False


class ToDoUpdate(BaseModel):
    """Schema for updating a todo"""
    title: Optional[str] = Field(None, min_length=3, max_length=100)
    is_done: Optional[bool] = None


class ToDo(BaseModel):
    """Schema for todo response"""
    id: int
    title: str
    is_done: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PaginatedToDoResponse(BaseModel):
    """Schema for paginated todo list response"""
    items: List[ToDo]
    total: int
    limit: int
    offset: int
