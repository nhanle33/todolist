from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date


class TagResponse(BaseModel):
    """Schema for tag in todo response"""
    id: int
    name: str
    color: str

    class Config:
        from_attributes = True


class ToDoCreate(BaseModel):
    """Schema for creating a new todo"""
    title: str = Field(..., min_length=3, max_length=100, description="Todo title")
    description: Optional[str] = Field(None, max_length=500, description="Todo description")
    is_done: bool = Field(False, description="Completion status")
    due_date: Optional[date] = Field(None, description="Deadline date (YYYY-MM-DD)")  # ✨ NEW
    tag_ids: Optional[List[int]] = Field(None, description="List of tag IDs")  # ✨ NEW


class ToDoUpdate(BaseModel):
    """Schema for updating a todo (full update)"""
    title: Optional[str] = Field(None, min_length=3, max_length=100, description="Todo title")
    description: Optional[str] = Field(None, max_length=500, description="Todo description")
    is_done: Optional[bool] = Field(None, description="Completion status")
    due_date: Optional[date] = Field(None, description="Deadline date")  # ✨ NEW
    tag_ids: Optional[List[int]] = Field(None, description="List of tag IDs")  # ✨ NEW


class ToDoPartialUpdate(BaseModel):
    """Schema for partial update (PATCH)"""
    title: Optional[str] = Field(None, min_length=3, max_length=100, description="Todo title")
    description: Optional[str] = Field(None, max_length=500, description="Todo description")
    is_done: Optional[bool] = Field(None, description="Completion status")
    due_date: Optional[date] = Field(None, description="Deadline date")  # ✨ NEW
    tag_ids: Optional[List[int]] = Field(None, description="List of tag IDs")  # ✨ NEW


class ToDoResponse(BaseModel):
    """Schema for todo response"""
    id: int
    title: str
    description: Optional[str]
    is_done: bool
    due_date: Optional[date]  # ✨ NEW
    tags: List[TagResponse] = []  # ✨ NEW
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PaginatedToDoResponse(BaseModel):
    """Schema for paginated todo list response"""
    items: List[ToDoResponse]
    total: int
    limit: int
    offset: int
