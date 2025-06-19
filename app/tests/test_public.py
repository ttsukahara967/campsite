import pytest

@pytest.mark.asyncio
async def test_register_and_login(async_client):
    # ユーザー登録
    response = await async_client.post("/api/register", json={
        "username": "testuser",
        "password": "testpass"
    })
    assert response.status_code == 200

    # ログイン
    response = await async_client.post("/api/admin/token", data={
        "username": "testuser",
        "password": "testpass"
    })
    assert response.status_code == 200
    token = response.json()["access_token"]
    assert token

@pytest.mark.asyncio
async def test_campsite_list(async_client):
    response = await async_client.get("/api/campsites")
    assert response.status_code == 200
