from typing import Optional
from sqlalchemy.orm import Session
from app.db import User
from app.core.security import hash_password, verify_password


class UserRepository:
    """Repository for managing users in database"""

    def __init__(self, db: Session):
        self.db = db

    def create(self, email: str, password: str) -> User:
        """Create a new user"""
        hashed_password = hash_password(password)
        user = User(email=email, hashed_password=hashed_password)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        return self.db.query(User).filter(User.email == email).first()

    def get_by_id(self, user_id: int) -> Optional[User]:
        """Get user by id"""
        return self.db.query(User).filter(User.id == user_id).first()

    def authenticate(self, email: str, password: str) -> Optional[User]:
        """Authenticate user with email and password"""
        user = self.get_by_email(email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user
