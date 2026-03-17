from typing import List, Optional
from sqlalchemy.orm import Session
from app.repositories.tag import TagRepository
from app.schemas import TagCreate, TagUpdate, TagResponse
from pydantic import BaseModel


class PaginatedTagResponse(BaseModel):
    """Schema for paginated tag list response"""
    items: List[TagResponse]
    total: int
    limit: int
    offset: int


class TagService:
    """Service for tag business logic"""

    def __init__(self, db: Session):
        self.repository = TagRepository(db)

    def create_tag(self, tag_create: TagCreate) -> TagResponse:
        """Create a new tag"""
        tag = self.repository.create(name=tag_create.name, color=tag_create.color)
        return TagResponse.from_orm(tag)

    def get_tag(self, tag_id: int) -> Optional[TagResponse]:
        """Get tag by id"""
        tag = self.repository.get_by_id(tag_id)
        if not tag:
            return None
        return TagResponse.from_orm(tag)

    def list_tags(self, limit: int = 100, offset: int = 0) -> PaginatedTagResponse:
        """List all tags with pagination"""
        tags, total = self.repository.get_all(limit, offset)
        return PaginatedTagResponse(
            items=[TagResponse.from_orm(t) for t in tags],
            total=total,
            limit=limit,
            offset=offset,
        )

    def update_tag(self, tag_id: int, tag_update: TagUpdate) -> Optional[TagResponse]:
        """Update a tag"""
        tag = self.repository.update(
            tag_id=tag_id,
            name=tag_update.name,
            color=tag_update.color,
        )
        if not tag:
            return None
        return TagResponse.from_orm(tag)

    def delete_tag(self, tag_id: int) -> bool:
        """Delete a tag"""
        return self.repository.delete(tag_id)
