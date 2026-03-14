from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.db import ToDo
from datetime import datetime


class ToDoRepository:
    """Repository for managing todos in database"""

    def __init__(self, db: Session):
        self.db = db

    def create(self, title: str, description: Optional[str] = None, is_done: bool = False) -> ToDo:
        """Create a new todo"""
        todo = ToDo(title=title, description=description, is_done=is_done)
        self.db.add(todo)
        self.db.commit()
        self.db.refresh(todo)
        return todo

    def get_by_id(self, todo_id: int) -> Optional[ToDo]:
        """Get todo by id"""
        return self.db.query(ToDo).filter(ToDo.id == todo_id).first()

    def get_all(
        self,
        is_done: Optional[bool] = None,
        q: Optional[str] = None,
        sort: str = "created_at",
        limit: int = 10,
        offset: int = 0,
    ) -> tuple[List[ToDo], int]:
        """Get all todos with filtering, searching, sorting and pagination"""
        query = self.db.query(ToDo)

        # Filter by is_done
        if is_done is not None:
            query = query.filter(ToDo.is_done == is_done)

        # Search by title or description
        if q:
            q_lower = f"%{q}%"
            from sqlalchemy import or_
            query = query.filter(
                or_(
                    ToDo.title.ilike(q_lower),
                    ToDo.description.ilike(q_lower)
                )
            )

        # Get total count before pagination
        total = query.count()

        # Sort
        if sort:
            if sort.startswith("-"):
                sort_field = sort[1:]
                reverse = True
            else:
                sort_field = sort
                reverse = False

            # Map sort field to column
            sort_column = getattr(ToDo, sort_field, None)
            if sort_column:
                if reverse:
                    query = query.order_by(desc(sort_column))
                else:
                    query = query.order_by(sort_column)

        # Pagination
        todos = query.offset(offset).limit(limit).all()

        return todos, total

    def update(
        self,
        todo_id: int,
        title: Optional[str] = None,
        description: Optional[str] = None,
        is_done: Optional[bool] = None,
    ) -> Optional[ToDo]:
        """Update a todo"""
        todo = self.get_by_id(todo_id)
        if not todo:
            return None

        if title is not None:
            todo.title = title
        if description is not None:
            todo.description = description
        if is_done is not None:
            todo.is_done = is_done

        todo.updated_at = datetime.now()
        self.db.commit()
        self.db.refresh(todo)
        return todo

    def delete(self, todo_id: int) -> bool:
        """Delete a todo"""
        todo = self.get_by_id(todo_id)
        if not todo:
            return False

        self.db.delete(todo)
        self.db.commit()
        return True
