from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.cooking import CookingSession, Favorite, Review
from app.models.recipe import Recipe
from app.models.user import User
from app.schemas.cooking import (
    CookingSessionOut,
    FavoriteOut,
    FinishCookingIn,
    StartCookingIn,
    UpdateProgressIn,
)

router = APIRouter(prefix="/cook", tags=["cook"])


@router.post("/start", response_model=CookingSessionOut, status_code=201)
def start(payload: StartCookingIn, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    recipe = db.get(Recipe, payload.recipe_id)
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    s = CookingSession(user_id=user.id, recipe_id=recipe.id)
    db.add(s)
    db.commit()
    db.refresh(s)
    return CookingSessionOut(id=s.id, recipe_id=s.recipe_id, current_step=s.current_step, is_finished=s.is_finished)


@router.get("/sessions/{session_id}", response_model=CookingSessionOut)
def get_session(session_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    s = db.get(CookingSession, session_id)
    if not s or s.user_id != user.id:
        raise HTTPException(status_code=404, detail="Session not found")
    return CookingSessionOut(id=s.id, recipe_id=s.recipe_id, current_step=s.current_step, is_finished=s.is_finished)


@router.put("/sessions/{session_id}", response_model=CookingSessionOut)
def update_progress(session_id: int, payload: UpdateProgressIn, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    s = db.get(CookingSession, session_id)
    if not s or s.user_id != user.id:
        raise HTTPException(status_code=404, detail="Session not found")
    if s.is_finished:
        raise HTTPException(status_code=400, detail="Session already finished")
    s.current_step = payload.current_step
    db.add(s)
    db.commit()
    db.refresh(s)
    return CookingSessionOut(id=s.id, recipe_id=s.recipe_id, current_step=s.current_step, is_finished=s.is_finished)


@router.post("/sessions/{session_id}/finish")
def finish(session_id: int, payload: FinishCookingIn, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    s = db.get(CookingSession, session_id)
    if not s or s.user_id != user.id:
        raise HTTPException(status_code=404, detail="Session not found")
    if s.is_finished:
        raise HTTPException(status_code=400, detail="Session already finished")

    s.is_finished = True
    s.finished_at = datetime.utcnow()

    # Upsert review: last review wins
    existing = db.query(Review).filter(Review.user_id == user.id, Review.recipe_id == s.recipe_id).first()
    if existing:
        existing.rating = payload.rating
        existing.comment = payload.comment
        db.add(existing)
    else:
        db.add(Review(user_id=user.id, recipe_id=s.recipe_id, rating=payload.rating, comment=payload.comment))

    # Increase popularity
    recipe = db.get(Recipe, s.recipe_id)
    if recipe:
        recipe.popularity = (recipe.popularity or 0) + 1
        db.add(recipe)

    db.add(s)
    db.commit()

    return {"ok": True}


@router.post("/favorites/{recipe_id}", response_model=FavoriteOut)
def toggle_favorite(recipe_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Allow favorite only if user has at least one finished session for this recipe
    cooked = (
        db.query(CookingSession)
        .filter(CookingSession.user_id == user.id, CookingSession.recipe_id == recipe_id, CookingSession.is_finished == True)
        .first()
    )
    if not cooked:
        raise HTTPException(status_code=400, detail="Можно добавить в избранное только приготовленные блюда")

    fav = db.query(Favorite).filter(Favorite.user_id == user.id, Favorite.recipe_id == recipe_id).first()
    if fav:
        db.delete(fav)
        db.commit()
        return FavoriteOut(recipe_id=recipe_id, is_favorite=False)
    db.add(Favorite(user_id=user.id, recipe_id=recipe_id))
    db.commit()
    return FavoriteOut(recipe_id=recipe_id, is_favorite=True)
