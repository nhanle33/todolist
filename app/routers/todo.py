from fastapi import APIRouter, HTTPException, Query, Depends
from sqlalchemy.orm import Session
from typing import Optional
from app.schemas import ToDoCreate, ToDoUpdate, ToDoPartialUpdate, ToDoResponse, PaginatedToDoResponse
from app.services import ToDoService
from app.db import get_db

router = APIRouter(
    prefix="/todos",
    tags=["todos"],
    responses={404: {"description": "Not found"}},
)


@router.post("", response_model=ToDoResponse, status_code=201)
def create_todo(todo: ToDoCreate, db: Session = Depends(get_db)):
    """Create a new todo"""
    service = ToDoService(db)
    return service.create_todo(todo)


@router.get("", response_model=PaginatedToDoResponse)
def list_todos(
    is_done: Optional[bool] = Query(None, description="Filter by is_done status"),
    q: Optional[str] = Query(None, description="Search by title or description"),
    sort: Optional[str] = Query("created_at", description="Sort by field (use - prefix for descending)"),
    limit: int = Query(10, ge=1, le=100, description="Items per page"),
    offset: int = Query(0, ge=0, description="Items to skip"),
    db: Session = Depends(get_db),
):
    """
    Get all todos with filtering, searching, sorting and pagination
    
    Uses real database pagination (not in-memory)
    """
    service = ToDoService(db)
    return service.list_todos(
        is_done=is_done,
        q=q,
        sort=sort,
        limit=limit,
        offset=offset,
    )


@router.get("/{todo_id}", response_model=ToDoResponse)
def get_todo(todo_id: int, db: Session = Depends(get_db)):
    """Get a specific todo by id"""
    service = ToDoService(db)
    todo = service.get_todo(todo_id)
    if not todo:
        raise HTTPException(status_code=404, detail=f"Todo with id {todo_id} not found")
    return todo


@router.put("/{todo_id}", response_model=ToDoResponse)
def update_todo(todo_id: int, todo_update: ToDoUpdate, db: Session = Depends(get_db)):
    """Update a todo (PUT - full update)"""
    service = ToDoService(db)
    todo = service.update_todo(todo_id, todo_update)
    if not todo:
        raise HTTPException(status_code=404, detail=f"Todo with id {todo_id} not found")
    return todo


@router.patch("/{todo_id}", response_model=ToDoResponse)
def partial_update_todo(todo_id: int, todo_update: ToDoPartialUpdate, db: Session = Depends(get_db)):
    """Partially update a todo (PATCH) - only update provided fields"""
    service = ToDoService(db)
    todo = service.partial_update_todo(todo_id, todo_update)
    if not todo:
        raise HTTPException(status_code=404, detail=f"Todo with id {todo_id} not found")
    return todo


@router.post("/{todo_id}/complete", response_model=ToDoResponse)
def mark_complete(todo_id: int, db: Session = Depends(get_db)):
    """Mark a todo as complete"""
    service = ToDoService(db)
    todo = service.mark_complete(todo_id)
    if not todo:
        raise HTTPException(status_code=404, detail=f"Todo with id {todo_id} not found")
    return todo


@router.delete("/{todo_id}", status_code=204)
def delete_todo(todo_id: int, db: Session = Depends(get_db)):
    """Delete a todo"""
    service = ToDoService(db)
    success = service.delete_todo(todo_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Todo with id {todo_id} not found")
    return None
