from fastapi import FastAPI, Depends
from routers import public, admin
from app.database.session import get_engine, get_session_maker, get_db

engine = get_engine()
session_maker = get_session_maker(engine)

app = FastAPI()

# 依存性注入の使い方例
def get_db_for_app():
    return get_db(session_maker)

app.dependency_overrides[get_db] = get_db_for_app

# router登録等はそのまま
app.include_router(public.router)
app.include_router(admin.router)
