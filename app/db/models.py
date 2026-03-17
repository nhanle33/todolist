from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Table, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


# Association table for many-to-many relationship between ToDo and Tag
todo_tag_association = Table(
    'todo_tags',
    Base.metadata,
    Column('todo_id', Integer, ForeignKey('todos.id', ondelete='CASCADE'), primary_key=True),
    Column('tag_id', Integer, ForeignKey('tags.id', ondelete='CASCADE'), primary_key=True)
)


class User(Base):
    """SQLAlchemy ORM model for users"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime, default=datetime.now, nullable=False, index=True)

    # Relationship
    todos = relationship("ToDo", back_populates="owner", cascade="all, delete-orphan")

    class Config:
        from_attributes = True


class ToDo(Base):
    """SQLAlchemy ORM model for todos"""
    __tablename__ = "todos"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=True)
    is_done = Column(Boolean, default=False, index=True)
    due_date = Column(Date, nullable=True, index=True)  # ✨ NEW: deadline
    created_at = Column(DateTime, default=datetime.now, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)
    
    # Foreign key
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Relationships
    owner = relationship("User", back_populates="todos")
    tags = relationship("Tag", secondary=todo_tag_association, back_populates="todos")  # ✨ NEW: many-to-many with tags

    class Config:
        from_attributes = True


class Tag(Base):
    """SQLAlchemy ORM model for tags"""
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False, unique=True, index=True)  # e.g., "work", "urgent", "personal"
    color = Column(String(7), default="#999999")  # Hex color code
    created_at = Column(DateTime, default=datetime.now, nullable=False)

    # Relationship
    todos = relationship("ToDo", secondary=todo_tag_association, back_populates="tags")

    class Config:
        from_attributes = True
