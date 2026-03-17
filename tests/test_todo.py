"""
Todo endpoint tests
"""
import pytest
from datetime import date, timedelta


class TestTodoCreate:
    """Test todo creation"""
    
    def test_create_todo_success(self, client, auth_headers):
        """Test successful todo creation"""
        response = client.post(
            "/api/v1/todos",
            headers=auth_headers,
            json={
                "title": "Learn FastAPI",
                "description": "Study FastAPI fundamentals"
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Learn FastAPI"
        assert data["description"] == "Study FastAPI fundamentals"
        assert data["is_done"] is False
        assert "id" in data
        assert "created_at" in data
    
    def test_create_todo_with_tags(self, client, auth_headers, test_tag):
        """Test creating todo with tags"""
        response = client.post(
            "/api/v1/todos",
            headers=auth_headers,
            json={
                "title": "Work task",
                "tag_ids": [test_tag["id"]]
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert len(data["tags"]) == 1
        assert data["tags"][0]["id"] == test_tag["id"]
    
    def test_create_todo_with_due_date(self, client, auth_headers):
        """Test creating todo with due date"""
        due_date_str = (date.today() + timedelta(days=5)).isoformat()
        
        response = client.post(
            "/api/v1/todos",
            headers=auth_headers,
            json={
                "title": "Future task",
                "due_date": due_date_str
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["due_date"] == due_date_str
    
    def test_create_todo_title_too_short(self, client, auth_headers):
        """Test todo creation with title too short"""
        response = client.post(
            "/api/v1/todos",
            headers=auth_headers,
            json={"title": "x"}
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_create_todo_no_auth(self, client):
        """Test creating todo without authentication"""
        response = client.post(
            "/api/v1/todos",
            json={"title": "Unauthorized todo"}
        )
        
        assert response.status_code == 403


class TestTodoList:
    """Test todo listing and filtering"""
    
    def test_list_todos_empty(self, client, auth_headers):
        """Test listing todos when none exist"""
        response = client.get(
            "/api/v1/todos",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert data["items"] == []
    
    def test_list_todos_success(self, client, auth_headers, test_todo):
        """Test listing todos"""
        response = client.get(
            "/api/v1/todos",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert len(data["items"]) == 1
        assert data["items"][0]["id"] == test_todo["id"]
    
    def test_list_todos_filter_by_status(self, client, auth_headers, test_todo):
        """Test filtering todos by completion status"""
        # Should return 1 incomplete todo
        response = client.get(
            "/api/v1/todos?is_done=false",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        
        # Should return 0 completed todos
        response = client.get(
            "/api/v1/todos?is_done=true",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
    
    def test_list_todos_search(self, client, auth_headers, test_todo):
        """Test searching todos"""
        response = client.get(
            "/api/v1/todos?q=Test",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
    
    def test_list_todos_pagination(self, client, auth_headers):
        """Test pagination"""
        # Create 5 todos
        for i in range(5):
            client.post(
                "/api/v1/todos",
                headers=auth_headers,
                json={"title": f"Todo {i+1}"}
            )
        
        # Get first 2
        response = client.get(
            "/api/v1/todos?limit=2&offset=0",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 5
        assert len(data["items"]) == 2
        assert data["limit"] == 2
        assert data["offset"] == 0
    
    def test_user_isolation(self, client, auth_headers, test_user_2):
        """Test that users can only see their own todos"""
        # Create todo as user 1
        response = client.post(
            "/api/v1/todos",
            headers=auth_headers,
            json={"title": "User 1 only"}
        )
        assert response.status_code == 201
        
        # Login as user 2
        user2_headers = {"Authorization": f"Bearer {test_user_2['token']}"}
        response = client.get(
            "/api/v1/todos",
            headers=user2_headers
        )
        
        # User 2 should not see user 1's todos
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0


class TestTodoDetail:
    """Test getting single todo"""
    
    def test_get_todo_success(self, client, auth_headers, test_todo):
        """Test getting a single todo"""
        response = client.get(
            f"/api/v1/todos/{test_todo['id']}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_todo["id"]
        assert data["title"] == test_todo["title"]
    
    def test_get_todo_not_found(self, client, auth_headers):
        """Test getting non-existent todo"""
        response = client.get(
            "/api/v1/todos/9999",
            headers=auth_headers
        )
        
        assert response.status_code == 404
    
    def test_get_todo_unauthorized(self, client, auth_headers, test_todo, test_user_2):
        """Test getting another user's todo"""
        user2_headers = {"Authorization": f"Bearer {test_user_2['token']}"}
        response = client.get(
            f"/api/v1/todos/{test_todo['id']}",
            headers=user2_headers
        )
        
        assert response.status_code == 404


class TestTodoUpdate:
    """Test updating todos"""
    
    def test_update_todo_success(self, client, auth_headers, test_todo):
        """Test updating a todo"""
        response = client.put(
            f"/api/v1/todos/{test_todo['id']}",
            headers=auth_headers,
            json={
                "title": "Updated Title",
                "is_done": True
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Title"
        assert data["is_done"] is True
    
    def test_partial_update_todo(self, client, auth_headers, test_todo):
        """Test partial update (PATCH)"""
        response = client.patch(
            f"/api/v1/todos/{test_todo['id']}",
            headers=auth_headers,
            json={"is_done": True}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["is_done"] is True
        assert data["title"] == test_todo["title"]  # Unchanged
    
    def test_update_todo_not_found(self, client, auth_headers):
        """Test updating non-existent todo"""
        response = client.put(
            "/api/v1/todos/9999",
            headers=auth_headers,
            json={"title": "New Title"}
        )
        
        assert response.status_code == 404


class TestTodoDelete:
    """Test deleting todos"""
    
    def test_delete_todo_success(self, client, auth_headers, test_todo):
        """Test deleting a todo"""
        todo_id = test_todo["id"]
        
        response = client.delete(
            f"/api/v1/todos/{todo_id}",
            headers=auth_headers
        )
        
        assert response.status_code == 204
        
        # Verify it's deleted
        response = client.get(
            f"/api/v1/todos/{todo_id}",
            headers=auth_headers
        )
        assert response.status_code == 404
    
    def test_delete_todo_not_found(self, client, auth_headers):
        """Test deleting non-existent todo"""
        response = client.delete(
            "/api/v1/todos/9999",
            headers=auth_headers
        )
        
        assert response.status_code == 404


class TestTodoSmartFiltering:
    """Test special filtering endpoints"""
    
    def test_today_endpoint(self, client, auth_headers):
        """Test /todos/today endpoint"""
        today = date.today().isoformat()
        
        # Create todo due today
        client.post(
            "/api/v1/todos",
            headers=auth_headers,
            json={
                "title": "Due today",
                "due_date": today
            }
        )
        
        # Create todo due tomorrow
        tomorrow = (date.today() + timedelta(days=1)).isoformat()
        client.post(
            "/api/v1/todos",
            headers=auth_headers,
            json={
                "title": "Due tomorrow",
                "due_date": tomorrow
            }
        )
        
        response = client.get(
            "/api/v1/todos/today",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["title"] == "Due today"
    
    def test_overdue_endpoint(self, client, auth_headers):
        """Test /todos/overdue endpoint"""
        yesterday = (date.today() - timedelta(days=1)).isoformat()
        
        # Create overdue todo
        client.post(
            "/api/v1/todos",
            headers=auth_headers,
            json={
                "title": "Overdue task",
                "due_date": yesterday
            }
        )
        
        response = client.get(
            "/api/v1/todos/overdue",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["title"] == "Overdue task"
    
    def test_today_excludes_completed(self, client, auth_headers):
        """Test that today endpoint excludes completed todos"""
        today = date.today().isoformat()
        
        # Create and complete a todo due today
        todo_response = client.post(
            "/api/v1/todos",
            headers=auth_headers,
            json={
                "title": "Complete this",
                "due_date": today
            }
        )
        todo_id = todo_response.json()["id"]
        
        # Mark as done
        client.patch(
            f"/api/v1/todos/{todo_id}",
            headers=auth_headers,
            json={"is_done": True}
        )
        
        response = client.get(
            "/api/v1/todos/today",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0  # Completed todos excluded
