from __future__ import annotations

import math
import re
from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.models.recipe import Recipe, RecipeIngredient


def normalize_ing(name: str) -> str:
    s = name.strip().lower()
    s = re.sub(r"\s+", " ", s)
    # very small naive normalization (rus)
    for suffix in ("ы", "и", "а", "я", "ов", "ев", "ого", "ому", "е"):
        if len(s) > 4 and s.endswith(suffix):
            s = s[: -len(suffix)]
            break
    return s


@dataclass
class RecipeMatch:
    recipe: Recipe
    score: float
    missing_ingredients: list[str]


class RecipeRecommender:
    def __init__(self, db: Session):
        self.db = db

    def search(
        self,
        user_ingredients: list[str],
        only_owned: bool = False,
        meal_type: str | None = None,
        max_time_minutes: int | None = None,
        max_kcal: int | None = None,
        difficulty: str | None = None,
        protein_g_min: float | None = None,
        fat_g_max: float | None = None,
        carbs_g_max: float | None = None,
        limit: int = 12,
    ) -> list[RecipeMatch]:
        have = {normalize_ing(i) for i in user_ingredients if i and i.strip()}
        if not have:
            return []

        q = self.db.query(Recipe)
        if meal_type:
            q = q.filter(Recipe.meal_type == meal_type)
        if max_time_minutes is not None:
            q = q.filter(Recipe.time_minutes <= max_time_minutes)
        if max_kcal is not None:
            q = q.filter(Recipe.kcal <= max_kcal)
        if difficulty:
            q = q.filter(Recipe.difficulty == difficulty)

        recipes = q.all()
        results: list[RecipeMatch] = []
        for r in recipes:
            ings = [normalize_ing(ri.ingredient.name) for ri in r.ingredients]
            if not ings:
                continue

            missing = sorted({i for i in ings if i not in have})
            if only_owned and missing:
                continue

            overlap = len(ings) - len(missing)
            overlap_ratio = overlap / max(1, len(ings))

            score = 50.0 * overlap_ratio
            score -= 7.0 * len(missing)

            # Slightly prefer more popular recipes
            score += min(10.0, math.log1p(max(0, r.popularity)))

            # macros soft constraints
            if protein_g_min is not None:
                score += 5.0 if float(r.protein_g) >= protein_g_min else -3.0
            if fat_g_max is not None:
                score += 3.0 if float(r.fat_g) <= fat_g_max else -3.0
            if carbs_g_max is not None:
                score += 3.0 if float(r.carbs_g) <= carbs_g_max else -3.0

            results.append(RecipeMatch(recipe=r, score=score, missing_ingredients=missing))

        results.sort(key=lambda x: x.score, reverse=True)
        return results[:limit]
