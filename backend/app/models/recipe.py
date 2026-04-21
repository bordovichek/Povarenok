from sqlalchemy import String, Integer, ForeignKey, LargeBinary, JSON, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.common import MealType, Difficulty


class Recipe(Base):
    __tablename__ = "recipes"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    meal_type: Mapped[MealType] = mapped_column(String(30), index=True)

    time_minutes: Mapped[int] = mapped_column(Integer, default=20, index=True)
    difficulty: Mapped[Difficulty] = mapped_column(String(30), default=Difficulty.easy)

    kcal: Mapped[int] = mapped_column(Integer, default=0)
    protein_g: Mapped[float] = mapped_column(Numeric(10, 2), default=0)
    fat_g: Mapped[float] = mapped_column(Numeric(10, 2), default=0)
    carbs_g: Mapped[float] = mapped_column(Numeric(10, 2), default=0)

    steps: Mapped[list] = mapped_column(JSON, default=list)

    image_bytes: Mapped[bytes | None] = mapped_column(LargeBinary, nullable=True)
    image_mime: Mapped[str] = mapped_column(String(40), default="image/webp", nullable=False)

    popularity: Mapped[int] = mapped_column(Integer, default=0, index=True)

    ingredients = relationship("RecipeIngredient", back_populates="recipe", cascade="all, delete-orphan")
    reviews = relationship("Review", back_populates="recipe", cascade="all, delete-orphan")
    favorites = relationship("Favorite", back_populates="recipe", cascade="all, delete-orphan")


class Ingredient(Base):
    __tablename__ = "ingredients"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), unique=True, index=True)

    recipes = relationship("RecipeIngredient", back_populates="ingredient")


class RecipeIngredient(Base):
    __tablename__ = "recipe_ingredients"

    id: Mapped[int] = mapped_column(primary_key=True)
    recipe_id: Mapped[int] = mapped_column(ForeignKey("recipes.id", ondelete="CASCADE"), index=True)
    ingredient_id: Mapped[int] = mapped_column(ForeignKey("ingredients.id", ondelete="CASCADE"), index=True)

    quantity: Mapped[float] = mapped_column(Numeric(10, 2), default=0)
    unit: Mapped[str] = mapped_column(String(30), default="", nullable=False)

    recipe = relationship("Recipe", back_populates="ingredients")
    ingredient = relationship("Ingredient", back_populates="recipes")
