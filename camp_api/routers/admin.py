from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from models.user import DBUser
from models.campsite import DBCampsite
from schemas.user import Token
from schemas.campsite import Campsite, CampsiteCreate
from core.security import create_access_token, verify_token
from database.session import get_db
import hashlib
from datetime import timedelta

router = APIRouter(prefix="/api/admin", tags=["admin"])

@router.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    result = await db.execute(DBUser.__table__.select().where(DBUser.username == form_data.username))
    user = result.fetchone()
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    hashed_input = hashlib.sha256(form_data.password.encode()).hexdigest()
    if user.hashed_password != hashed_input:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    access_token = create_access_token(data={"sub": user.username}, expires_delta=timedelta(minutes=60))
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/campsites", response_model=Campsite)
async def create_campsite(campsite: CampsiteCreate, db: AsyncSession = Depends(get_db), token: str = Depends(verify_token)):
    db_campsite = DBCampsite(
        name=campsite.name,
        description=campsite.description,
        location=campsite.location,
        prefecture=campsite.prefecture,
        price_min=campsite.price_min,
        price_max=campsite.price_max,
        pet_friendly=campsite.pet_friendly,
        tags=','.join(campsite.tags)
    )
    db.add(db_campsite)
    await db.commit()
    await db.refresh(db_campsite)
    return db_campsite

@router.put("/campsites/{campsite_id}", response_model=Campsite)
async def update_campsite(campsite_id: int, campsite: CampsiteCreate, db: AsyncSession = Depends(get_db), token: str = Depends(verify_token)):
    result = await db.execute(DBCampsite.__table__.select().where(DBCampsite.id == campsite_id))
    db_campsite = result.fetchone()
    if not db_campsite:
        raise HTTPException(status_code=404, detail="Campsite not found")
    update_data = campsite.dict()
    if "tags" in update_data:
        update_data["tags"] = ','.join(update_data["tags"])
    await db.execute(DBCampsite.__table__.update().where(DBCampsite.id == campsite_id).values(**update_data))
    await db.commit()
    result = await db.execute(DBCampsite.__table__.select().where(DBCampsite.id == campsite_id))
    updated = result.fetchone()
    return updated

@router.delete("/campsites/{campsite_id}")
async def delete_campsite(campsite_id: int, db: AsyncSession = Depends(get_db), token: str = Depends(verify_token)):
    result = await db.execute(DBCampsite.__table__.select().where(DBCampsite.id == campsite_id))
    db_campsite = result.fetchone()
    if not db_campsite:
        raise HTTPException(status_code=404, detail="Campsite not found")
    await db.execute(DBCampsite.__table__.delete().where(DBCampsite.id == campsite_id))
    await db.commit()
    return {"message": "Deleted"}
