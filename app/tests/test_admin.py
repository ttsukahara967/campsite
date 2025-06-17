# tests/test_admin.py
import pytest
from tests.factories import UserFactory

def test_admin_create_user(client, db):
    response = client.post("/admin/users/", json={
        "username": "adminuser",
        "email": "admin@example.com",
        "password": "secure123"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "admin@example.com"

def test_admin_get_users(client, db):
    UserFactory.create_batch(3)
    response = client.get("/admin/users/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

# tests/test_admin.py

def test_admin_create_user_with_token(auth_client):
    response = auth_client.post("/admin/users/", json={
        "username": "newuser",
        "email": "newuser@example.com",
        "password": "testpass123"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "newuser@example.com"

def test_admin_list_users_with_token(auth_client, db):
    response = auth_client.get("/admin/users/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_admin_unauthorized_access(client):
    response = client.get("/admin/users/")
    assert response.status_code == 401  # 認証されていない
