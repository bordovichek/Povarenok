import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base
from app.main import create_app

# Import models to register with Base
from app.models.user import User  # noqa: F401
from app.models.pantry import PantryItem  # noqa: F401
from app.models.recipe import Recipe, Ingredient, RecipeIngredient  # noqa: F401
from app.models.cooking import CookingSession, Review, Favorite, PasswordResetToken  # noqa: F401


@pytest.fixture(scope="session")
def test_db_url() -> str:
    return os.getenv(
        "TEST_DATABASE_URL",
        os.getenv("DATABASE_URL", "postgresql+psycopg2://postgres:postgres@localhost:5432/smart_cookbook_test"),
    )


@pytest.fixture(scope="session")
def engine(test_db_url):
    engine = create_engine(test_db_url, pool_pre_ping=True)
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    from sqlalchemy.orm import sessionmaker
    from app.seed.seed_recipes import seed_if_empty

    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    db = SessionLocal()
    try:
        seed_if_empty(db)
    finally:
        db.close()

    return engine


@pytest.fixture()
def client(engine):
    app = create_app()

    # Override dependency
    from app.core.database import get_db

    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)
