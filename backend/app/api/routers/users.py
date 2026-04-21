from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.cooking import CookingSession, Favorite, Review
from app.models.recipe import Recipe
from app.models.user import User
from app.schemas.user import CookingHistoryOut, FavoriteListOut, ReviewOut, UpdateProfileIn

router = APIRouter(prefix="/users", tags=["users"])


@router.put("/me")
def update_profile(payload: UpdateProfileIn, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    user.profile_constraints = (payload.profile_constraints or "").strip()
    db.add(user)
    db.commit()
    return {"ok": True}


@router.get("/me/history", response_model=list[CookingHistoryOut])
def history(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    sessions = (
        db.query(CookingSession)
        .filter(CookingSession.user_id == user.id)
        .order_by(CookingSession.started_at.desc())
        .limit(200)
        .all()
    )
    # map recipe titles
    recipe_ids = {s.recipe_id for s in sessions}
    title_by_id = {r.id: r.title for r in db.query(Recipe).filter(Recipe.id.in_(recipe_ids)).all()} if recipe_ids else {}

    return [
        CookingHistoryOut(
            session_id=s.id,
            recipe_id=s.recipe_id,
            recipe_title=title_by_id.get(s.recipe_id, ""),
            started_at=s.started_at,
            finished_at=s.finished_at,
            is_finished=s.is_finished,
        )
        for s in sessions
    ]


@router.get("/me/reviews", response_model=list[ReviewOut])
def reviews(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    rs = (
        db.query(Review)
        .filter(Review.user_id == user.id)
        .order_by(Review.created_at.desc())
        .limit(200)
        .all()
    )
    recipe_ids = {r.recipe_id for r in rs}
    title_by_id = {r.id: r.title for r in db.query(Recipe).filter(Recipe.id.in_(recipe_ids)).all()} if recipe_ids else {}

    return [
        ReviewOut(
            recipe_id=r.recipe_id,
            recipe_title=title_by_id.get(r.recipe_id, ""),
            rating=r.rating,
            comment=r.comment,
            created_at=r.created_at,
        )
        for r in rs
    ]


@router.get("/me/favorites", response_model=list[FavoriteListOut])
def favorites(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    fs = (
        db.query(Favorite)
        .filter(Favorite.user_id == user.id)
        .order_by(Favorite.created_at.desc())
        .limit(200)
        .all()
    )
    recipe_ids = {f.recipe_id for f in fs}
    title_by_id = {r.id: r.title for r in db.query(Recipe).filter(Recipe.id.in_(recipe_ids)).all()} if recipe_ids else {}

    return [
        FavoriteListOut(
            recipe_id=f.recipe_id,
            recipe_title=title_by_id.get(f.recipe_id, ""),
            created_at=f.created_at,
        )
        for f in fs
    ]
