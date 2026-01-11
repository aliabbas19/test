
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
    try:
        heroes_map = {}
        
        # 1. Get Weekly Heroes (from StarBank)
        # Query users with banked stars >= 4 (Manhaji)
        weekly_champions = (
            db.query(User, StarBank)
            .join(StarBank, User.id == StarBank.user_id)
            .filter(StarBank.banked_stars >= 4)
            .order_by(StarBank.banked_stars.desc())
            .all()
        )
        
        for user, bank in weekly_champions:
            heroes_map[user.id] = HeroResponse(
                user_id=user.id,
                full_name=user.full_name or user.username,
                profile_image=user.profile_image,
                banked_stars=bank.banked_stars,
                rank_type='hero',
                class_name=user.class_name,
                section_name=user.section_name
            )

        # 2. Get Superheroes (Enrichment Champions)
        # Using existing service logic
        from app.services.champion_service import get_superhero_champions
        superhero_list, _ = get_superhero_champions(db)
        
        for hero_data in superhero_list:
            uid = hero_data['id']
            # If user already exists (is also a weekly hero), upgrade them or keep them?
            # Usually Superhero > Hero. Let's mark them as superhero.
            # But we need their stars. For superhero, stars might be 10 (fixed) or actual count.
            # get_superhero_champions returns list of dicts, doesn't imply star count in the dict clearly for 'banked_stars'.
            # We'll use 10 as visual indicator or fetch if needed.
            
            if uid in heroes_map:
                heroes_map[uid].rank_type = 'superhero'
            else:
                # New entry
                # Need to fetch User object if not in hero_data fully or rely on hero_data
                # hero_data has basic info.
                heroes_map[uid] = HeroResponse(
                    user_id=uid,
                    full_name=hero_data['full_name'] or hero_data['username'],
                    profile_image=hero_data['profile_image'],
                    banked_stars=10, # Visual indicator for superhero
                    rank_type='superhero',
                    class_name=None, # Service doesn't return class currently, could fetch or ignore
                    section_name=None
                )
                
        return list(heroes_map.values())
    except Exception as e:
        print(f"Error fetching heroes: {e}")
        return []
