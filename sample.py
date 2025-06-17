from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy import Column, Integer, String, Boolean, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from jose import JWTError, jwt
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
import hashlib

load_dotenv()

app = FastAPI()

# ------------------------------
# JWT Config
# ------------------------------

SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/admin/token")

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str = Depends(oauth2_scheme), db: Session = Depends(lambda: next(get_db()))):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user = db.query(DBUser).filter(DBUser.username == username).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid user")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

# ------------------------------
# Database setup (MySQL)
# ------------------------------

MYSQL_USER = os.getenv("MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "password")
MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
MYSQL_PORT = os.getenv("MYSQL_PORT", "3306")
MYSQL_DB = os.getenv("MYSQL_DB", "campsite")

SQLALCHEMY_DATABASE_URL = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ------------------------------
# DB Models
# ------------------------------

class DBCampsite(Base):
    __tablename__ = "campsites"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String, nullable=True)
    location = Column(String)
    prefecture = Column(String)
    price_min = Column(Integer)
    price_max = Column(Integer)
    pet_friendly = Column(Boolean)
    tags = Column(String)  # comma-separated

class DBUser(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)

Base.metadata.create_all(bind=engine)

# ------------------------------
# Models (for request/response)
# ------------------------------

class CampsiteBase(BaseModel):
    name: str
    description: Optional[str] = None
    location: str
    prefecture: str
    price_min: int
    price_max: int
    pet_friendly: bool
    tags: List[str] = []

class CampsiteCreate(CampsiteBase):
    pass

class Campsite(CampsiteBase):
    id: int

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str

class UserCreate(BaseModel):
    username: str
    password: str

# ------------------------------
# Dependency
# ------------------------------

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ------------------------------
# Public Endpoints
# ------------------------------

@app.post("/api/register")
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(DBUser).filter(DBUser.username == user.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")
    hashed = hashlib.sha256(user.password.encode()).hexdigest()
    new_user = DBUser(username=user.username, hashed_password=hashed)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User registered successfully"}

@app.get("/api/campsites", response_model=List[Campsite])
def list_campsites(
    keyword: Optional[str] = None,
    prefecture: Optional[str] = None,
    pet_friendly: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    query = db.query(DBCampsite)
    if keyword:
        query = query.filter(DBCampsite.name.contains(keyword))
    if prefecture:
        query = query.filter(DBCampsite.prefecture == prefecture)
    if pet_friendly is not None:
        query = query.filter(DBCampsite.pet_friendly == pet_friendly)
    results = query.all()
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
    ) for c in results]

@app.get("/api/campsites/{campsite_id}", response_model=Campsite)
def get_campsite(campsite_id: int, db: Session = Depends(get_db)):
    c = db.query(DBCampsite).filter(DBCampsite.id == campsite_id).first()
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

# ------------------------------
# Admin Endpoints (JWT protected)
# ------------------------------

@app.post("/api/admin/token", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(DBUser).filter(DBUser.username == form_data.username).first()
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    hashed_input = hashlib.sha256(form_data.password.encode()).hexdigest()
    if user.hashed_password != hashed_input:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    access_token = create_access_token(data={"sub": user.username}, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/api/admin/campsites", response_model=Campsite)
def create_campsite(campsite: CampsiteCreate, db: Session = Depends(get_db), token: str = Depends(verify_token)):
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
    db.commit()
    db.refresh(db_campsite)
    return db_campsite

@app.put("/api/admin/campsites/{campsite_id}", response_model=Campsite)
def update_campsite(campsite_id: int, campsite: CampsiteCreate, db: Session = Depends(get_db), token: str = Depends(verify_token)):
    db_campsite = db.query(DBCampsite).filter(DBCampsite.id == campsite_id).first()
    if not db_campsite:
        raise HTTPException(status_code=404, detail="Campsite not found")
    for field, value in campsite.dict().items():
        if field == "tags":
            setattr(db_campsite, field, ','.join(value))
        else:
            setattr(db_campsite, field, value)
    db.commit()
    return db_campsite

@app.delete("/api/admin/campsites/{campsite_id}")
def delete_campsite(campsite_id: int, db: Session = Depends(get_db), token: str = Depends(verify_token)):
    db_campsite = db.query(DBCampsite).filter(DBCampsite.id == campsite_id).first()
    if not db_campsite:
        raise HTTPException(status_code=404, detail="Campsite not found")
    db.delete(db_campsite)
    db.commit()
    return {"message": "Deleted"}

