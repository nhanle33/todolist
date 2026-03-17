from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from app.schemas import UserRegister, UserLogin, UserResponse, TokenResponse, CurrentUser
from app.services.auth import AuthService
from app.core.security import decode_access_token
from app.db import get_db, User

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
    responses={401: {"description": "Unauthorized"}},
)

security = HTTPBearer()


async def get_current_user(credentials = Depends(security), db: Session = Depends(get_db)) -> User:
    """Get current user from token"""
    token = credentials.credentials
    
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user_id = int(payload.get("sub"))
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found or inactive")
    
    return user


@router.post("/register", response_model=UserResponse, status_code=201)
def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """Register a new user"""
    service = AuthService(db)
    try:
        return service.register(user_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login", response_model=TokenResponse)
def login(login_data: UserLogin, db: Session = Depends(get_db)):
    """Login user and get access token"""
    service = AuthService(db)
    try:
        return service.login(login_data)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))


@router.get("/me", response_model=CurrentUser)
def get_me(current_user: User = Depends(get_current_user)):
    """Get current user info"""
    return CurrentUser(
        id=current_user.id,
        email=current_user.email,
        is_active=current_user.is_active,
        created_at=current_user.created_at
    )
