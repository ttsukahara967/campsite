from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from models.user import DBUser
from models.campsite import DBCampsite
from schemas.user import UserCreate
from schemas.campsite import Campsite, CampsiteCreate
from database.session import get_db
import hashlib
from typing import Optional, List

router = APIRouter(prefix="/api", tags=["public"])

@router.post("/register")
async def register_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(DBUser.__table__.select().where(DBUser.username == user.username))
    existing = result.fetchone()
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")
    hashed = hashlib.sha256(user.password.encode()).hexdigest()
    new_user = DBUser(username=user.username, hashed_password=hashed)
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return {"message": "User registered successfully"}

@router.get("/campsites", response_model=List[Campsite])
async def list_campsites(keyword: Optional[str] = None, prefecture: Optional[str] = None, pet_friendly: Optional[bool] = None, db: AsyncSession = Depends(get_db)):
    query = DBCampsite.__table__.select()
    if keyword:
        query = query.where(DBCampsite.name.contains(keyword))
    if prefecture:
        query = query.where(DBCampsite.prefecture == prefecture)
    if pet_friendly is not None:
        query = query.where(DBCampsite.pet_friendly == pet_friendly)
    result = await db.execute(query)
    rows = result.fetchall()
    return [Campsite(
        id=c.id,
        name=c.name,
        description=c.description,
        location=c.location,
        prefecture=c.prefecture,
        price_min=c.price_min,
        price_max=c.price_max,
        pet_friendly=c.pet_friendly,
        tags=c.tags.split(",") if c.tags else []
    ) for c in rows]

@router.get("/campsites/{campsite_id}", response_model=Campsite)
async def get_campsite(campsite_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(DBCampsite.__table__.select().where(DBCampsite.id == campsite_id))
    c = result.fetchone()
    if not c:
        raise HTTPException(status_code=404, detail="Campsite not found")
    return Campsite(
        id=c.id,
        name=c.name,
        description=c.description,
        location=c.location,
        prefecture=c.prefecture,
        price_min=c.price_min,
        price_max=c.price_max,
        pet_friendly=c.pet_friendly,
        tags=c.tags.split(",") if c.tags else []
    )
