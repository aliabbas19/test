"""
Pydantic schemas
"""
from app.schemas.user import User, UserCreate, UserUpdate, UserInDB
from app.schemas.video import Video, VideoCreate, VideoUpdate
from app.schemas.comment import Comment, CommentCreate, CommentUpdate
from app.schemas.rating import RatingCriterion, RatingCriterionCreate, VideoRating, VideoRatingCreate
from app.schemas.message import Message, MessageCreate
from app.schemas.auth import Token, TokenData, Login

__all__ = [
    "User", "UserCreate", "UserUpdate", "UserInDB",
    "Video", "VideoCreate", "VideoUpdate",
    "Comment", "CommentCreate", "CommentUpdate",
    "RatingCriterion", "RatingCriterionCreate", "VideoRating", "VideoRatingCreate",
    "Message", "MessageCreate",
    "Token", "TokenData", "Login",
]
