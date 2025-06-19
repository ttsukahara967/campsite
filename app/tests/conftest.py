import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from httpx import AsyncClient
from app.main import app
from app.database.base import Base
from app.database.session import get_db

ASYNC_DB_URL = "sqlite+aiosqlite:///:memory:"

@pytest_asyncio.fixture(scope="function")
async def async_client():
    # テスト用engine/session
    engine = create_async_engine(ASYNC_DB_URL, echo=False, future=True)
    TestingSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    # テスト用DBの初期化
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    # テスト用 get_db（sessionmaker直渡し版）を作る
    async def override_get_db():
        async with TestingSessionLocal() as session:
            yield session

    # ここでFastAPI側のget_dbを完全に上書き
    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

    await engine.dispose()
