import pytest

@pytest.mark.asyncio
async def test_admin_create_campsite(async_client):
    # 1. 管理者ユーザーを作成
    await async_client.post("/api/register", json={
        "username": "adminuser",
        "password": "adminpass"
    })
    # 2. トークン取得
    resp = await async_client.post("/api/admin/token", data={
        "username": "adminuser",
        "password": "adminpass"
    })
    assert resp.status_code == 200
    token = resp.json()["access_token"]
    # 3. 管理APIにトークン付きでPOST
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "name": "富士山キャンプ場",
        "description": "絶景！",
        "location": "山梨県富士吉田市",
        "prefecture": "山梨",
        "price_min": 3000,
        "price_max": 7000,
        "pet_friendly": True,
        "tags": ["富士山", "絶景"]
    }
    resp = await async_client.post("/api/admin/campsites", json=data, headers=headers)
    assert resp.status_code == 200
    assert resp.json()["name"] == "富士山キャンプ場"

@pytest.mark.asyncio
async def test_admin_update_and_delete_campsite(async_client):
    # 管理者ユーザーを作成しログイン
    await async_client.post("/api/register", json={
        "username": "adminuser2",
        "password": "adminpass2"
    })
    resp = await async_client.post("/api/admin/token", data={
        "username": "adminuser2",
        "password": "adminpass2"
    })
    token = resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    # キャンプ場登録
    post_data = {
        "name": "テストキャンプ場",
        "description": "テスト説明",
        "location": "東京都",
        "prefecture": "東京",
        "price_min": 2000,
        "price_max": 4000,
        "pet_friendly": False,
        "tags": ["テスト"]
    }
    resp = await async_client.post("/api/admin/campsites", json=post_data, headers=headers)
    campsite_id = resp.json()["id"]

    # 更新
    update_data = post_data.copy()
    update_data["name"] = "更新後キャンプ場"
    resp = await async_client.put(f"/api/admin/campsites/{campsite_id}", json=update_data, headers=headers)
    assert resp.status_code == 200
    assert resp.json()["name"] == "更新後キャンプ場"

    # 削除
    resp = await async_client.delete(f"/api/admin/campsites/{campsite_id}", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["message"] == "Deleted"
