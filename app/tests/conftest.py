# tests/conftest.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import json
from tests.factories import UserFactory
from app.core.security import get_password_hash

from app.main import app
from app.database import Base, get_db

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"  # SQLiteで簡易に

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session", autouse=True)
def create_test_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def db():
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture()
def client(db):
    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)


@pytest.fixture
def auth_client(client, db):
    from tests.factories import UserFactory

    password = "adminpass"
    admin_user = UserFactory(
        username="adminuser",
        email="admin@example.com",
        hashed_password=get_password_hash(password),
        is_admin=True,
        sqlalchemy_session=db,  # ここで db セッションを渡す
    )
    db.commit()

    response = client.post("/admin/token", data={
        "username": admin_user.username,
        "password": password,
    })
    assert response.status_code == 200
    token = response.json()["access_token"]
    client.headers = {
        **client.headers,
        "Authorization": f"Bearer {token}"
    }
    return client
