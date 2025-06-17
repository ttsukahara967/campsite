from fastapi import FastAPI
from routers import public, admin
from database.session import Base, engine

app = FastAPI()

# Include routers
app.include_router(public.router)
app.include_router(admin.router)

# Uncomment for table creation at startup (dev only)
# async def init_db():
#     async with engine.begin() as conn:
#         await conn.run_sync(Base.metadata.create_all)
# import asyncio; asyncio.run(init_db())
