from fastapi import APIRouter, HTTPException, Query, Depends, Security
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from typing import Optional
from app.schemas import ToDoCreate, ToDoUpdate, ToDoPartialUpdate, ToDoResponse, PaginatedToDoResponse
from app.services import ToDoService
from app.services.auth import AuthService
from app.db import get_db
from app.db.models import User
from app.core.security import decode_access_token

router = APIRouter(
    prefix="/todos",
    tags=["todos"],
    responses={404: {"description": "Not found"}},
)

security = HTTPBearer()


async def get_current_user(
    credentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    """Dependency to get current authenticated user"""
    token = credentials.credentials
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    auth_service = AuthService(db)
    user = auth_service.get_current_user_by_id(int(user_id))
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    
    return user


@router.post("", response_model=ToDoResponse, status_code=201)
def create_todo(
    todo: ToDoCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new todo"""
    service = ToDoService(db)
    return service.create_todo(current_user.id, todo)


@router.get("", response_model=PaginatedToDoResponse)
def list_todos(
    is_done: Optional[bool] = Query(None, description="Filter by is_done status"),
    q: Optional[str] = Query(None, description="Search by title or description"),
    sort: Optional[str] = Query("created_at", description="Sort by field (use - prefix for descending)"),
    limit: int = Query(10, ge=1, le=100, description="Items per page"),
    offset: int = Query(0, ge=0, description="Items to skip"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get all todos with filtering, searching, sorting and pagination
    
    Uses real database pagination (not in-memory)
    """
    service = ToDoService(db)
    return service.list_todos(
        current_user.id,
        is_done=is_done,
        q=q,
        sort=sort,
        limit=limit,
        offset=offset,
    )


@router.get("/overdue", response_model=PaginatedToDoResponse)
def get_overdue_todos(
    limit: int = Query(10, ge=1, le=100, description="Items per page"),
    offset: int = Query(0, ge=0, description="Items to skip"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get overdue todos (due_date < today and not done)"""
    service = ToDoService(db)
    return service.get_overdue(current_user.id, limit, offset)


@router.get("/today", response_model=PaginatedToDoResponse)
def get_today_todos(
    limit: int = Query(10, ge=1, le=100, description="Items per page"),
    offset: int = Query(0, ge=0, description="Items to skip"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get today's todos (due_date = today and not done)"""
    service = ToDoService(db)
    return service.get_today(current_user.id, limit, offset)


@router.get("/deleted", response_model=PaginatedToDoResponse)
def get_deleted_todos(
    limit: int = Query(10, ge=1, le=100, description="Items per page"),
    offset: int = Query(0, ge=0, description="Items to skip"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get deleted todos (soft delete)"""
    service = ToDoService(db)
    return service.get_deleted(current_user.id, limit, offset)


@router.get("/{todo_id}", response_model=ToDoResponse)
def get_todo(
    todo_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a specific todo by id"""
    service = ToDoService(db)
    todo = service.get_todo(todo_id, current_user.id)
    if not todo:
        raise HTTPException(status_code=404, detail=f"Todo with id {todo_id} not found")
    return todo


@router.put("/{todo_id}", response_model=ToDoResponse)
def update_todo(
    todo_id: int,
    todo_update: ToDoUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a todo (PUT - full update)"""
    service = ToDoService(db)
    todo = service.update_todo(todo_id, current_user.id, todo_update)
    if not todo:
        raise HTTPException(status_code=404, detail=f"Todo with id {todo_id} not found")
    return todo


@router.patch("/{todo_id}", response_model=ToDoResponse)
def partial_update_todo(
    todo_id: int,
    todo_update: ToDoPartialUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Partially update a todo (PATCH) - only update provided fields"""
    service = ToDoService(db)
    todo = service.partial_update_todo(todo_id, current_user.id, todo_update)
    if not todo:
        raise HTTPException(status_code=404, detail=f"Todo with id {todo_id} not found")
    return todo


@router.post("/{todo_id}/complete", response_model=ToDoResponse)
def mark_complete(
    todo_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Mark a todo as complete"""
    service = ToDoService(db)
    todo = service.mark_complete(todo_id, current_user.id)
    if not todo:
        raise HTTPException(status_code=404, detail=f"Todo with id {todo_id} not found")
    return todo


@router.post("/{todo_id}/restore", response_model=ToDoResponse)
def restore_todo(
    todo_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Restore a soft-deleted todo"""
    service = ToDoService(db)
    todo = service.restore_todo(todo_id, current_user.id)
    if not todo:
        raise HTTPException(status_code=404, detail=f"Deleted todo with id {todo_id} not found")
    return todo


@router.delete("/{todo_id}", status_code=204)
def delete_todo(
    todo_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Soft delete a todo"""
    service = ToDoService(db)
    success = service.delete_todo(todo_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Todo with id {todo_id} not found")
    return None
