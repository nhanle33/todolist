from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


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
    created_at = Column(DateTime, default=datetime.now, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)
    
    # Foreign key
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Relationship
    owner = relationship("User", back_populates="todos")

    class Config:
        from_attributes = True
