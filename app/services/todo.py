from typing import List, Optional
from sqlalchemy.orm import Session
from app.repositories.database import ToDoRepository
from app.schemas import ToDoCreate, ToDoUpdate, ToDoPartialUpdate, ToDoResponse, PaginatedToDoResponse


class ToDoService:
    """Service for todo business logic"""

    def __init__(self, db: Session):
        self.repository = ToDoRepository(db)

    def create_todo(self, owner_id: int, todo_create: ToDoCreate) -> ToDoResponse:
        """Create a new todo"""
        todo = self.repository.create(
            owner_id=owner_id,
            title=todo_create.title,
            description=todo_create.description,
            is_done=todo_create.is_done,
            due_date=todo_create.due_date,  # ✨ NEW
            tag_ids=todo_create.tag_ids,  # ✨ NEW
        )
        return ToDoResponse.from_orm(todo)

    def get_todo(self, todo_id: int, owner_id: int) -> Optional[ToDoResponse]:
        """Get todo by id (must belong to owner)"""
        todo = self.repository.get_by_id(todo_id, owner_id)
        if not todo:
            return None
        return ToDoResponse.from_orm(todo)

    def list_todos(
        self,
        owner_id: int,
        is_done: Optional[bool] = None,
        q: Optional[str] = None,
        sort: str = "created_at",
        limit: int = 10,
        offset: int = 0,
    ) -> PaginatedToDoResponse:
        """List todos owned by user with filtering, searching, sorting and pagination"""
        todos, total = self.repository.get_all(
            owner_id=owner_id,
            is_done=is_done,
            q=q,
            sort=sort,
            limit=limit,
            offset=offset,
        )

        return PaginatedToDoResponse(
            items=[ToDoResponse.from_orm(t) for t in todos],
            total=total,
            limit=limit,
            offset=offset,
        )

    def update_todo(self, todo_id: int, owner_id: int, todo_update: ToDoUpdate) -> Optional[ToDoResponse]:
        """Update a todo (PUT - full update)"""
        todo = self.repository.update(
            todo_id=todo_id,
            owner_id=owner_id,
            title=todo_update.title,
            description=todo_update.description,
            is_done=todo_update.is_done,
            due_date=todo_update.due_date,  # ✨ NEW
            tag_ids=todo_update.tag_ids,  # ✨ NEW
        )
        if not todo:
            return None
        return ToDoResponse.from_orm(todo)

    def partial_update_todo(self, todo_id: int, owner_id: int, todo_update: ToDoPartialUpdate) -> Optional[ToDoResponse]:
        """Partial update a todo (PATCH)"""
        todo = self.repository.update(
            todo_id=todo_id,
            owner_id=owner_id,
            title=todo_update.title,
            description=todo_update.description,
            is_done=todo_update.is_done,
            due_date=todo_update.due_date,  # ✨ NEW
            tag_ids=todo_update.tag_ids,  # ✨ NEW
        )
        if not todo:
            return None
        return ToDoResponse.from_orm(todo)

    def mark_complete(self, todo_id: int, owner_id: int) -> Optional[ToDoResponse]:
        """Mark a todo as complete"""
        todo = self.repository.update(todo_id=todo_id, owner_id=owner_id, is_done=True)
        if not todo:
            return None
        return ToDoResponse.from_orm(todo)

    def delete_todo(self, todo_id: int, owner_id: int) -> bool:
        """Delete a todo (must belong to owner)"""
        return self.repository.delete(todo_id, owner_id)

    def get_overdue(self, owner_id: int, limit: int = 10, offset: int = 0) -> PaginatedToDoResponse:
        """Get overdue todos (due_date < today and not done)"""
        todos, total = self.repository.get_overdue(owner_id, limit, offset)
        return PaginatedToDoResponse(
            items=[ToDoResponse.from_orm(t) for t in todos],
            total=total,
            limit=limit,
            offset=offset,
        )

    def get_today(self, owner_id: int, limit: int = 10, offset: int = 0) -> PaginatedToDoResponse:
        """Get today's todos (due_date = today and not done)"""
        todos, total = self.repository.get_today(owner_id, limit, offset)
        return PaginatedToDoResponse(
            items=[ToDoResponse.from_orm(t) for t in todos],
            total=total,
            limit=limit,
            offset=offset,
        )
