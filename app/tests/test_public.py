# tests/test_public.py
def test_health_check(client):
    response = client.get("/public/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

# tests/test_public.py

def test_public_access_no_auth_required(client):
    response = client.get("/public/health")
    assert response.status_code == 200
