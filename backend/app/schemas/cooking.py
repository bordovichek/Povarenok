from pydantic import BaseModel, Field


class StartCookingIn(BaseModel):
    recipe_id: int


class CookingSessionOut(BaseModel):
    id: int
    recipe_id: int
    current_step: int
    is_finished: bool


class UpdateProgressIn(BaseModel):
    current_step: int = Field(ge=0)


class FinishCookingIn(BaseModel):
    rating: int = Field(ge=1, le=5)
    comment: str = Field(default="", max_length=2000)


class FavoriteOut(BaseModel):
    recipe_id: int
    is_favorite: bool
