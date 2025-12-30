
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.star_bank import StarBank
from app.models.user import User
from pydantic import BaseModel

router = APIRouter()

class HeroResponse(BaseModel):
    user_id: int
    full_name: str
    profile_image: str | None = None
    banked_stars: int
    rank_type: str  # 'superhero' or 'hero'
    class_name: str | None = None
    section_name: str | None = None

    class Config:
        from_attributes = True

@router.get("/", response_model=List[HeroResponse])
def get_heroes(db: Session = Depends(get_db)):
    # Query users with banked stars >= 5, joined with StarBank
    results = (
        db.query(User, StarBank)
        .join(StarBank, User.id == StarBank.user_id)
        .filter(StarBank.banked_stars >= 5)
        .order_by(StarBank.banked_stars.desc())
        .all()
    )
    
    heroes = []
    for user, bank in results:
        rank_type = 'superhero' if bank.banked_stars >= 10 else 'hero'
        heroes.append(HeroResponse(
            user_id=user.id,
            full_name=user.full_name or user.username,
            profile_image=user.profile_image,
            banked_stars=bank.banked_stars,
            rank_type=rank_type,
            class_name=user.class_name,
            section_name=user.section_name
        ))
        
    return heroes
