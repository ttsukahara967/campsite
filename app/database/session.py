from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from core.config import DATABASE_URL

def get_engine(database_url=None):
    url = database_url or DATABASE_URL
    return create_async_engine(url, echo=True, future=True)

def get_session_maker(engine):
    return sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_db(session_maker):  # 必ずsession_makerを渡す
    async with session_maker() as session:
        yield session
