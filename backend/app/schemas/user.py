from datetime import datetime

from pydantic import BaseModel, Field


class UpdateProfileIn(BaseModel):
    profile_constraints: str = Field(default="", max_length=4000)


class CookingHistoryOut(BaseModel):
    session_id: int
    recipe_id: int
    recipe_title: str
    started_at: datetime
    finished_at: datetime | None
    is_finished: bool


class ReviewOut(BaseModel):
    recipe_id: int
    recipe_title: str
    rating: int
    comment: str
    created_at: datetime


class FavoriteListOut(BaseModel):
    recipe_id: int
    recipe_title: str
    created_at: datetime
