from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.recipe import Recipe
from app.models.user import User
from app.schemas.recipes import (
    PersonalizedRecipeOut,
    RecipeCardOut,
    RecipeDetailOut,
    RecipeSearchIn,
    RecipeSearchResultOut,
)
from app.services.recipe_generator import personalize_steps
from app.services.recipe_recommender import RecipeRecommender

router = APIRouter(prefix="/recipes", tags=["recipes"])


@router.get("/popular")
def popular(db: Session = Depends(get_db)):
    # Top 6 per meal_type by popularity
    data = {}
    for meal in ("breakfast", "lunch", "dinner", "any"):
        recs = (
            db.query(Recipe)
            .filter(Recipe.meal_type == meal)
            .order_by(Recipe.popularity.desc(), Recipe.id.asc())
            .limit(6)
            .all()
        )
        data[meal] = [
            RecipeCardOut(
                id=r.id,
                title=r.title,
                meal_type=r.meal_type,
                time_minutes=r.time_minutes,
                difficulty=r.difficulty,
                kcal=r.kcal,
                protein_g=float(r.protein_g),
                fat_g=float(r.fat_g),
                carbs_g=float(r.carbs_g),
            )
            for r in recs
        ]
    return data


@router.post("/search", response_model=list[RecipeSearchResultOut])
def search(payload: RecipeSearchIn, db: Session = Depends(get_db)):
    recommender = RecipeRecommender(db)
    matches = recommender.search(
        user_ingredients=payload.ingredients,
        only_owned=payload.only_owned,
        meal_type=payload.meal_type,
        max_time_minutes=payload.max_time_minutes,
        max_kcal=payload.max_kcal,
        difficulty=payload.difficulty,
        protein_g_min=payload.protein_g_min,
        fat_g_max=payload.fat_g_max,
        carbs_g_max=payload.carbs_g_max,
        limit=payload.limit,
    )
    return [
        RecipeSearchResultOut(
            recipe=RecipeCardOut(
                id=m.recipe.id,
                title=m.recipe.title,
                meal_type=m.recipe.meal_type,
                time_minutes=m.recipe.time_minutes,
                difficulty=m.recipe.difficulty,
                kcal=m.recipe.kcal,
                protein_g=float(m.recipe.protein_g),
                fat_g=float(m.recipe.fat_g),
                carbs_g=float(m.recipe.carbs_g),
            ),
            score=m.score,
            missing_ingredients=m.missing_ingredients,
        )
        for m in matches
    ]


@router.get("/{recipe_id}", response_model=RecipeDetailOut)
def recipe_detail(recipe_id: int, db: Session = Depends(get_db)):
    recipe = db.get(Recipe, recipe_id)
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return RecipeDetailOut(
        id=recipe.id,
        title=recipe.title,
        meal_type=recipe.meal_type,
        time_minutes=recipe.time_minutes,
        difficulty=recipe.difficulty,
        kcal=recipe.kcal,
        protein_g=float(recipe.protein_g),
        fat_g=float(recipe.fat_g),
        carbs_g=float(recipe.carbs_g),
        ingredients=[
            {"name": ri.ingredient.name, "quantity": float(ri.quantity), "unit": ri.unit}
            for ri in recipe.ingredients
        ],
        steps=recipe.steps or [],
    )


@router.get("/{recipe_id}/image")
def recipe_image(recipe_id: int, db: Session = Depends(get_db)):
    recipe = db.get(Recipe, recipe_id)
    if not recipe or not recipe.image_bytes:
        raise HTTPException(status_code=404, detail="Image not found")
    return Response(content=recipe.image_bytes, media_type=recipe.image_mime)


@router.post("/{recipe_id}/personalize", response_model=PersonalizedRecipeOut)
def personalize(recipe_id: int, payload: RecipeSearchIn, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    recipe = db.get(Recipe, recipe_id)
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

    # Compute missing ingredients for shopping list
    from app.services.recipe_recommender import normalize_ing

    have = {normalize_ing(i) for i in payload.ingredients}
    recipe_ings = [normalize_ing(ri.ingredient.name) for ri in recipe.ingredients]
    shopping = sorted({i for i in recipe_ings if i not in have})

    constraints = (payload.user_constraints or "").strip() or user.profile_constraints
    steps, notes = personalize_steps(recipe.steps or [], constraints)

    return PersonalizedRecipeOut(
        recipe_id=recipe.id,
        title=recipe.title,
        steps=steps,
        shopping_list=shopping,
        notes=notes,
    )
