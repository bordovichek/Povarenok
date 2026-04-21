"""initial

Revision ID: 0001
Revises: 
Create Date: 2026-03-03
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("password_hash", sa.String(length=500), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("profile_constraints", sa.Text(), nullable=False, server_default=""),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    op.create_table(
        "pantry_items",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("category", sa.String(length=80), nullable=False, server_default=""),
        sa.Column("quantity", sa.Numeric(10, 2), nullable=False, server_default="0"),
        sa.Column("unit", sa.String(length=30), nullable=False, server_default=""),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_pantry_items_user_id", "pantry_items", ["user_id"], unique=False)
    op.create_index("ix_pantry_items_name", "pantry_items", ["name"], unique=False)

    op.create_table(
        "recipes",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("meal_type", sa.String(length=30), nullable=False),
        sa.Column("time_minutes", sa.Integer(), nullable=False, server_default="20"),
        sa.Column("difficulty", sa.String(length=30), nullable=False, server_default="easy"),
        sa.Column("kcal", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("protein_g", sa.Numeric(10, 2), nullable=False, server_default="0"),
        sa.Column("fat_g", sa.Numeric(10, 2), nullable=False, server_default="0"),
        sa.Column("carbs_g", sa.Numeric(10, 2), nullable=False, server_default="0"),
        sa.Column("steps", sa.JSON(), nullable=False, server_default=sa.text("'[]'::json")),
        sa.Column("image_bytes", sa.LargeBinary(), nullable=True),
        sa.Column("image_mime", sa.String(length=40), nullable=False, server_default="image/webp"),
        sa.Column("popularity", sa.Integer(), nullable=False, server_default="0"),
    )
    op.create_index("ix_recipes_title", "recipes", ["title"], unique=False)
    op.create_index("ix_recipes_meal_type", "recipes", ["meal_type"], unique=False)
    op.create_index("ix_recipes_time_minutes", "recipes", ["time_minutes"], unique=False)
    op.create_index("ix_recipes_popularity", "recipes", ["popularity"], unique=False)

    op.create_table(
        "ingredients",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=120), nullable=False),
    )
    op.create_index("ix_ingredients_name", "ingredients", ["name"], unique=True)

    op.create_table(
        "recipe_ingredients",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("recipe_id", sa.Integer(), sa.ForeignKey("recipes.id", ondelete="CASCADE"), nullable=False),
        sa.Column("ingredient_id", sa.Integer(), sa.ForeignKey("ingredients.id", ondelete="CASCADE"), nullable=False),
        sa.Column("quantity", sa.Numeric(10, 2), nullable=False, server_default="0"),
        sa.Column("unit", sa.String(length=30), nullable=False, server_default=""),
    )
    op.create_index("ix_recipe_ingredients_recipe_id", "recipe_ingredients", ["recipe_id"], unique=False)
    op.create_index("ix_recipe_ingredients_ingredient_id", "recipe_ingredients", ["ingredient_id"], unique=False)

    op.create_table(
        "cooking_sessions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("recipe_id", sa.Integer(), sa.ForeignKey("recipes.id", ondelete="CASCADE"), nullable=False),
        sa.Column("started_at", sa.DateTime(), nullable=False),
        sa.Column("finished_at", sa.DateTime(), nullable=True),
        sa.Column("current_step", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("is_finished", sa.Boolean(), nullable=False, server_default=sa.text("false")),
    )
    op.create_index("ix_cooking_sessions_user_id", "cooking_sessions", ["user_id"], unique=False)
    op.create_index("ix_cooking_sessions_recipe_id", "cooking_sessions", ["recipe_id"], unique=False)
    op.create_index("ix_cooking_sessions_started_at", "cooking_sessions", ["started_at"], unique=False)
    op.create_index("ix_cooking_sessions_is_finished", "cooking_sessions", ["is_finished"], unique=False)

    op.create_table(
        "reviews",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("recipe_id", sa.Integer(), sa.ForeignKey("recipes.id", ondelete="CASCADE"), nullable=False),
        sa.Column("rating", sa.Integer(), nullable=False),
        sa.Column("comment", sa.Text(), nullable=False, server_default=""),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_reviews_user_id", "reviews", ["user_id"], unique=False)
    op.create_index("ix_reviews_recipe_id", "reviews", ["recipe_id"], unique=False)

    op.create_table(
        "favorites",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("recipe_id", sa.Integer(), sa.ForeignKey("recipes.id", ondelete="CASCADE"), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.UniqueConstraint("user_id", "recipe_id", name="uq_fav_user_recipe"),
    )
    op.create_index("ix_favorites_user_id", "favorites", ["user_id"], unique=False)
    op.create_index("ix_favorites_recipe_id", "favorites", ["recipe_id"], unique=False)

    op.create_table(
        "password_reset_tokens",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("token_jti", sa.String(length=64), nullable=False),
        sa.Column("is_used", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("expires_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_password_reset_tokens_user_id", "password_reset_tokens", ["user_id"], unique=False)
    op.create_index("ix_password_reset_tokens_token_jti", "password_reset_tokens", ["token_jti"], unique=True)
    op.create_index("ix_password_reset_tokens_expires_at", "password_reset_tokens", ["expires_at"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_password_reset_tokens_expires_at", table_name="password_reset_tokens")
    op.drop_index("ix_password_reset_tokens_token_jti", table_name="password_reset_tokens")
    op.drop_index("ix_password_reset_tokens_user_id", table_name="password_reset_tokens")
    op.drop_table("password_reset_tokens")

    op.drop_index("ix_favorites_recipe_id", table_name="favorites")
    op.drop_index("ix_favorites_user_id", table_name="favorites")
    op.drop_table("favorites")

    op.drop_index("ix_reviews_recipe_id", table_name="reviews")
    op.drop_index("ix_reviews_user_id", table_name="reviews")
    op.drop_table("reviews")

    op.drop_index("ix_cooking_sessions_is_finished", table_name="cooking_sessions")
    op.drop_index("ix_cooking_sessions_started_at", table_name="cooking_sessions")
    op.drop_index("ix_cooking_sessions_recipe_id", table_name="cooking_sessions")
    op.drop_index("ix_cooking_sessions_user_id", table_name="cooking_sessions")
    op.drop_table("cooking_sessions")

    op.drop_index("ix_recipe_ingredients_ingredient_id", table_name="recipe_ingredients")
    op.drop_index("ix_recipe_ingredients_recipe_id", table_name="recipe_ingredients")
    op.drop_table("recipe_ingredients")

    op.drop_index("ix_ingredients_name", table_name="ingredients")
    op.drop_table("ingredients")

    op.drop_index("ix_recipes_popularity", table_name="recipes")
    op.drop_index("ix_recipes_time_minutes", table_name="recipes")
    op.drop_index("ix_recipes_meal_type", table_name="recipes")
    op.drop_index("ix_recipes_title", table_name="recipes")
    op.drop_table("recipes")

    op.drop_index("ix_pantry_items_name", table_name="pantry_items")
    op.drop_index("ix_pantry_items_user_id", table_name="pantry_items")
    op.drop_table("pantry_items")

    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
