from typing import List, Optional
from sqlalchemy.orm import Session
from app.db import Tag


class TagRepository:
    """Repository for managing tags in database"""

    def __init__(self, db: Session):
        self.db = db

    def create(self, name: str, color: str = "#999999") -> Tag:
        """Create a new tag"""
        tag = Tag(name=name, color=color)
        self.db.add(tag)
        self.db.commit()
        self.db.refresh(tag)
        return tag

    def get_by_id(self, tag_id: int) -> Optional[Tag]:
        """Get tag by id"""
        return self.db.query(Tag).filter(Tag.id == tag_id).first()

    def get_by_name(self, name: str) -> Optional[Tag]:
        """Get tag by name"""
        return self.db.query(Tag).filter(Tag.name == name).first()

    def get_all(self, limit: int = 100, offset: int = 0) -> tuple[List[Tag], int]:
        """Get all tags"""
        query = self.db.query(Tag).order_by(Tag.name)
        total = query.count()
        tags = query.offset(offset).limit(limit).all()
        return tags, total

    def update(self, tag_id: int, name: Optional[str] = None, color: Optional[str] = None) -> Optional[Tag]:
        """Update a tag"""
        tag = self.get_by_id(tag_id)
        if not tag:
            return None

        if name is not None:
            tag.name = name
        if color is not None:
            tag.color = color

        self.db.commit()
        self.db.refresh(tag)
        return tag

    def delete(self, tag_id: int) -> bool:
        """Delete a tag"""
        tag = self.get_by_id(tag_id)
        if not tag:
            return False

        self.db.delete(tag)
        self.db.commit()
        return True
