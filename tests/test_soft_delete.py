"""
Soft delete tests (Cấp 8)
"""
import pytest
from datetime import date


class TestSoftDelete:
    """Test soft delete functionality"""
    
    def test_delete_todo_soft_delete(self, client, auth_headers, test_todo):
        """Test that delete uses soft delete (deleted_at)"""
        todo_id = test_todo["id"]
        
        # Delete the todo
        response = client.delete(
            f"/api/v1/todos/{todo_id}",
            headers=auth_headers
        )
        
        assert response.status_code == 204
        
        # Todo should not appear in normal list
        response = client.get(
            "/api/v1/todos",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert all(t["id"] != todo_id for t in data["items"])
    
    def test_get_deleted_todos(self, client, auth_headers):
        """Test retrieving deleted todos"""
        # Create two todos
        todo1_response = client.post(
            "/api/v1/todos",
            headers=auth_headers,
            json={"title": "Todo 1"}
        )
        todo1_id = todo1_response.json()["id"]
        
        todo2_response = client.post(
            "/api/v1/todos",
            headers=auth_headers,
            json={"title": "Todo 2"}
        )
        todo2_id = todo2_response.json()["id"]
        
        # Delete first todo
        client.delete(
            f"/api/v1/todos/{todo1_id}",
            headers=auth_headers
        )
        
        # Get deleted todos
        response = client.get(
            "/api/v1/todos/deleted",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert len(data["items"]) == 1
        assert data["items"][0]["id"] == todo1_id
        assert data["items"][0]["title"] == "Todo 1"
        assert data["items"][0]["deleted_at"] is not None
    
    def test_restore_deleted_todo(self, client, auth_headers, test_todo):
        """Test restoring a deleted todo"""
        todo_id = test_todo["id"]
        
        # Delete the todo
        client.delete(
            f"/api/v1/todos/{todo_id}",
            headers=auth_headers
        )
        
        # Restore it
        response = client.post(
            f"/api/v1/todos/{todo_id}/restore",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == todo_id
        assert data["deleted_at"] is None  # No longer deleted
        
        # Should appear in normal list again
        response = client.get(
            "/api/v1/todos",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["id"] == todo_id
    
    def test_restore_non_existent_deleted_todo(self, client, auth_headers):
        """Test restoring non-existent delete todo"""
        response = client.post(
            "/api/v1/todos/9999/restore",
            headers=auth_headers
        )
        
        assert response.status_code == 404
    
    def test_deleted_todos_excluded_from_filtering(self, client, auth_headers):
        """Test that deleted todos are excluded from filtering"""
        # Create todos with different states
        todo1_response = client.post(
            "/api/v1/todos",
            headers=auth_headers,
            json={"title": "Complete task"}
        )
        todo1_id = todo1_response.json()["id"]
        
        todo2_response = client.post(
            "/api/v1/todos",
            headers=auth_headers,
            json={"title": "Incomplete task"}
        )
        todo2_id = todo2_response.json()["id"]
        
        # Complete first todo
        client.patch(
            f"/api/v1/todos/{todo1_id}",
            headers=auth_headers,
            json={"is_done": True}
        )
        
        # Delete incomplete todo
        client.delete(
            f"/api/v1/todos/{todo2_id}",
            headers=auth_headers
        )
        
        # Incomplete todos should not include deleted one
        response = client.get(
            "/api/v1/todos?is_done=false",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
    
    def test_deleted_todos_excluded_from_search(self, client, auth_headers):
        """Test that deleted todos don't appear in search"""
        # Create todo
        todo_response = client.post(
            "/api/v1/todos",
            headers=auth_headers,
            json={"title": "Important task"}
        )
        todo_id = todo_response.json()["id"]
        
        # Search should find it
        response = client.get(
            "/api/v1/todos?q=Important",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        
        # Delete it
        client.delete(
            f"/api/v1/todos/{todo_id}",
            headers=auth_headers
        )
        
        # Search should not find it anymore
        response = client.get(
            "/api/v1/todos?q=Important",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
    
    def test_deleted_todos_excluded_from_today(self, client, auth_headers):
        """Test that deleted todos don't appear in today endpoint"""
        today = date.today().isoformat()
        
        # Create todo due today
        todo_response = client.post(
            "/api/v1/todos",
            headers=auth_headers,
            json={
                "title": "Due today",
                "due_date": today
            }
        )
        todo_id = todo_response.json()["id"]
        
        # Should appear in today endpoint
        response = client.get(
            "/api/v1/todos/today",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        
        # Delete it
        client.delete(
            f"/api/v1/todos/{todo_id}",
            headers=auth_headers
        )
        
        # Should not appear anymore
        response = client.get(
            "/api/v1/todos/today",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
    
    def test_deleted_todos_excluded_from_overdue(self, client, auth_headers):
        """Test that deleted todos don't appear in overdue endpoint"""
        from datetime import timedelta
        
        yesterday = (date.today() - timedelta(days=1)).isoformat()
        
        # Create overdue todo
        todo_response = client.post(
            "/api/v1/todos",
            headers=auth_headers,
            json={
                "title": "Overdue task",
                "due_date": yesterday
            }
        )
        todo_id = todo_response.json()["id"]
        
        # Should appear in overdue endpoint
        response = client.get(
            "/api/v1/todos/overdue",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        
        # Delete it
        client.delete(
            f"/api/v1/todos/{todo_id}",
            headers=auth_headers
        )
        
        # Should not appear anymore
        response = client.get(
            "/api/v1/todos/overdue",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
    
    def test_user_isolation_on_deleted_todos(self, client, auth_headers, test_user_2):
        """Test that users only see their own deleted todos"""
        # Create todo as user 1
        todo_response = client.post(
            "/api/v1/todos",
            headers=auth_headers,
            json={"title": "User 1 todo"}
        )
        todo_id = todo_response.json()["id"]
        
        # Delete as user 1
        client.delete(
            f"/api/v1/todos/{todo_id}",
            headers=auth_headers
        )
        
        # User 2 should not see it in deleted list
        user2_headers = {"Authorization": f"Bearer {test_user_2['token']}"}
        response = client.get(
            "/api/v1/todos/deleted",
            headers=user2_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
    
    def test_pagination_on_deleted_todos(self, client, auth_headers):
        """Test pagination on deleted todos"""
        # Create and delete 5 todos
        for i in range(5):
            todo_response = client.post(
                "/api/v1/todos",
                headers=auth_headers,
                json={"title": f"Todo {i+1}"}
            )
            todo_id = todo_response.json()["id"]
            client.delete(
                f"/api/v1/todos/{todo_id}",
                headers=auth_headers
            )
        
        # Get first 2 deleted
        response = client.get(
            "/api/v1/todos/deleted?limit=2&offset=0",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 5
        assert len(data["items"]) == 2
        assert data["limit"] == 2
        assert data["offset"] == 0
