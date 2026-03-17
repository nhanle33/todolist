"""
Tag endpoint tests
"""
import pytest


class TestTagCreate:
    """Test tag creation"""
    
    def test_create_tag_success(self, client, auth_headers):
        """Test successful tag creation"""
        response = client.post(
            "/api/v1/tags",
            headers=auth_headers,
            json={
                "name": "work",
                "color": "#FF5733"
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "work"
        assert data["color"] == "#FF5733"
        assert "id" in data
        assert "created_at" in data
    
    def test_create_tag_default_color(self, client, auth_headers):
        """Test creating tag with default color"""
        response = client.post(
            "/api/v1/tags",
            headers=auth_headers,
            json={"name": "important"}
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["color"] == "#999999"  # Default gray
    
    def test_create_tag_duplicate_name(self, client, auth_headers):
        """Test creating tag with duplicate name fails"""
        # Create first tag
        client.post(
            "/api/v1/tags",
            headers=auth_headers,
            json={"name": "work"}
        )
        
        # Try to create duplicate
        response = client.post(
            "/api/v1/tags",
            headers=auth_headers,
            json={"name": "work"}
        )
        
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"].lower()
    
    def test_create_tag_no_auth(self, client):
        """Test creating tag without authentication"""
        response = client.post(
            "/api/v1/tags",
            json={"name": "work"}
        )
        
        assert response.status_code == 403


class TestTagList:
    """Test tag listing"""
    
    def test_list_tags_empty(self, client, auth_headers):
        """Test listing when no tags exist"""
        response = client.get(
            "/api/v1/tags",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert data["items"] == []
    
    def test_list_tags_success(self, client, auth_headers, test_tag):
        """Test listing tags"""
        response = client.get(
            "/api/v1/tags",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert len(data["items"]) == 1
        assert data["items"][0]["name"] == test_tag["name"]
    
    def test_list_tags_pagination(self, client, auth_headers):
        """Test tag pagination"""
        # Create 5 tags
        for i in range(5):
            client.post(
                "/api/v1/tags",
                headers=auth_headers,
                json={"name": f"tag{i+1}"}
            )
        
        # Get first 2
        response = client.get(
            "/api/v1/tags?limit=2&offset=0",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 5
        assert len(data["items"]) == 2
    
    def test_tags_are_global(self, client, auth_headers, test_user_2, test_tag):
        """Test that all users can see all tags"""
        user2_headers = {"Authorization": f"Bearer {test_user_2['token']}"}
        
        response = client.get(
            "/api/v1/tags",
            headers=user2_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["id"] == test_tag["id"]


class TestTagDetail:
    """Test getting single tag"""
    
    def test_get_tag_success(self, client, auth_headers, test_tag):
        """Test getting a single tag"""
        response = client.get(
            f"/api/v1/tags/{test_tag['id']}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_tag["id"]
        assert data["name"] == test_tag["name"]
    
    def test_get_tag_not_found(self, client, auth_headers):
        """Test getting non-existent tag"""
        response = client.get(
            "/api/v1/tags/9999",
            headers=auth_headers
        )
        
        assert response.status_code == 404


class TestTagUpdate:
    """Test updating tags"""
    
    def test_update_tag_name(self, client, auth_headers, test_tag):
        """Test updating tag name"""
        response = client.put(
            f"/api/v1/tags/{test_tag['id']}",
            headers=auth_headers,
            json={"name": "personal"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "personal"
    
    def test_update_tag_color(self, client, auth_headers, test_tag):
        """Test updating tag color"""
        response = client.put(
            f"/api/v1/tags/{test_tag['id']}",
            headers=auth_headers,
            json={"color": "#FF0000"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["color"] == "#FF0000"
        assert data["name"] == test_tag["name"]  # Unchanged
    
    def test_update_tag_both_fields(self, client, auth_headers, test_tag):
        """Test updating both name and color"""
        response = client.put(
            f"/api/v1/tags/{test_tag['id']}",
            headers=auth_headers,
            json={
                "name": "updated",
                "color": "#00FF00"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "updated"
        assert data["color"] == "#00FF00"
    
    def test_update_tag_not_found(self, client, auth_headers):
        """Test updating non-existent tag"""
        response = client.put(
            "/api/v1/tags/9999",
            headers=auth_headers,
            json={"name": "new"}
        )
        
        assert response.status_code == 404


class TestTagDelete:
    """Test deleting tags"""
    
    def test_delete_tag_success(self, client, auth_headers, test_tag):
        """Test deleting a tag"""
        tag_id = test_tag["id"]
        
        response = client.delete(
            f"/api/v1/tags/{tag_id}",
            headers=auth_headers
        )
        
        assert response.status_code == 204
        
        # Verify it's deleted
        response = client.get(
            f"/api/v1/tags/{tag_id}",
            headers=auth_headers
        )
        assert response.status_code == 404
    
    def test_delete_tag_not_found(self, client, auth_headers):
        """Test deleting non-existent tag"""
        response = client.delete(
            "/api/v1/tags/9999",
            headers=auth_headers
        )
        
        assert response.status_code == 404
    
    def test_delete_tag_cascade_to_todos(self, client, auth_headers, test_tag):
        """Test that deleting tag doesn't break todos"""
        # Create todo with tag
        todo_response = client.post(
            "/api/v1/todos",
            headers=auth_headers,
            json={
                "title": "Tagged todo",
                "tag_ids": [test_tag["id"]]
            }
        )
        todo_id = todo_response.json()["id"]
        
        # Delete tag
        client.delete(
            f"/api/v1/tags/{test_tag['id']}",
            headers=auth_headers
        )
        
        # Todo should still exist but without the tag
        response = client.get(
            f"/api/v1/todos/{todo_id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == todo_id
        assert data["tags"] == []  # Tag removed but todo intact
