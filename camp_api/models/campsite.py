from sqlalchemy import Column, Integer, String, Boolean
from database.session import Base

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
    