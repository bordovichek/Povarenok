from pydantic import BaseModel, Field


class RecipeCardOut(BaseModel):
    id: int
    title: str
    meal_type: str
    time_minutes: int
    difficulty: str
    kcal: int
    protein_g: float
    fat_g: float
    carbs_g: float


class IngredientOut(BaseModel):
    name: str
    quantity: float
    unit: str


class RecipeDetailOut(RecipeCardOut):
    ingredients: list[IngredientOut]
    steps: list[str]


class RecipeSearchIn(BaseModel):
    ingredients: list[str] = Field(min_length=1, description="List of ingredients the user has")
    only_owned: bool = False
    meal_type: str | None = None
    max_time_minutes: int | None = None
    max_kcal: int | None = None
    difficulty: str | None = None
    protein_g_min: float | None = None
    fat_g_max: float | None = None
    carbs_g_max: float | None = None
    user_constraints: str | None = None
    limit: int = Field(default=12, ge=1, le=50)


class RecipeSearchResultOut(BaseModel):
    recipe: RecipeCardOut
    score: float
    missing_ingredients: list[str]


class PersonalizedRecipeOut(BaseModel):
    recipe_id: int
    title: str
    steps: list[str]
    shopping_list: list[str]
    notes: list[str]
