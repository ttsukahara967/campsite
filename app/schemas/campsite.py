from pydantic import BaseModel
from typing import List, Optional

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
