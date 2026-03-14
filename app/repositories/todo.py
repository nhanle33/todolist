from typing import List, Optional
from datetime import datetime


class ToDoRepository:
    """Repository for managing todos in memory"""

    def __init__(self):
        self.todos: List[dict] = []
        self.next_id: int = 1

    def create(self, title: str, is_done: bool = False) -> dict:
        """Create a new todo"""
        now = datetime.now()
        todo = {
            "id": self.next_id,
            "title": title,
            "is_done": is_done,
            "created_at": now,
            "updated_at": now,
        }
        self.todos.append(todo)
        self.next_id += 1
        return todo

    def get_by_id(self, todo_id: int) -> Optional[dict]:
        """Get todo by id"""
        return next((t for t in self.todos if t["id"] == todo_id), None)

    def get_all(self) -> List[dict]:
        """Get all todos"""
        return self.todos.copy()

    def update(self, todo_id: int, title: Optional[str] = None, is_done: Optional[bool] = None) -> Optional[dict]:
        """Update a todo"""
        todo = self.get_by_id(todo_id)
        if not todo:
            return None

        if title is not None:
            todo["title"] = title
        if is_done is not None:
            todo["is_done"] = is_done

        todo["updated_at"] = datetime.now()
        return todo

    def delete(self, todo_id: int) -> bool:
        """Delete a todo"""
        todo = self.get_by_id(todo_id)
        if not todo:
            return False

        self.todos = [t for t in self.todos if t["id"] != todo_id]
        return True


# Global repository instance
todo_repository = ToDoRepository()
