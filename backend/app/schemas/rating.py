"""
Rating schemas
"""
from pydantic import BaseModel
from typing import Dict, Optional


class RatingCriterionBase(BaseModel):
    name: str
    key: str
    video_type: str  # 'منهجي' or 'اثرائي'


class RatingCriterionCreate(RatingCriterionBase):
    pass


class RatingCriterion(RatingCriterionBase):
    id: int
    
    class Config:
        from_attributes = True


class VideoRatingCreate(BaseModel):
    video_id: int
    ratings: Dict[str, int]  # {criterion_key: 1 or 0}


class VideoRating(BaseModel):
    video_id: int
    total_stars: int
    max_stars: int
    ratings: Dict[str, int]
