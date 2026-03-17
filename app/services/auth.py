from sqlalchemy.orm import Session
from app.repositories.user import UserRepository
from app.schemas import UserRegister, UserLogin, UserResponse, TokenResponse, CurrentUser
from app.core.security import create_access_token, decode_access_token
from app.db.models import User
from typing import Optional


class AuthService:
    """Service for authentication"""

    def __init__(self, db: Session):
        self.repository = UserRepository(db)

    def register(self, user_data: UserRegister) -> UserResponse:
        """Register a new user"""
        # Check if user already exists
        existing_user = self.repository.get_by_email(user_data.email)
        if existing_user:
            raise ValueError("Email already registered")
        
        # Create new user
        user = self.repository.create(
            email=user_data.email,
            password=user_data.password
        )
        return UserResponse.from_orm(user)

    def login(self, login_data: UserLogin) -> TokenResponse:
        """Login user and return access token"""
        # Authenticate user
        user = self.repository.authenticate(
            email=login_data.email,
            password=login_data.password
        )
        if not user:
            raise ValueError("Invalid email or password")
        
        # Create access token
        access_token = create_access_token(data={"sub": str(user.id)})
        return TokenResponse(access_token=access_token)

    def get_current_user(self, token: str) -> Optional[CurrentUser]:
        """Get current user from token"""
        payload = decode_access_token(token)
        if not payload:
            return None
        
        user_id = int(payload.get("sub"))
        # In a real app, would query DB, but for now just return ID
        return {"user_id": user_id}

    def get_current_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID from database"""
        return self.repository.get_by_id(user_id)
