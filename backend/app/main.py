from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routers import auth, cook, pantry, recipes, users
from app.core.config import settings


def create_app() -> FastAPI:
    app = FastAPI(title=settings.app_name)

    origins = [o.strip() for o in settings.cors_origins.split(",") if o.strip()]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins if origins else ["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(auth.router, prefix=settings.api_prefix)
    app.include_router(pantry.router, prefix=settings.api_prefix)
    app.include_router(recipes.router, prefix=settings.api_prefix)
    app.include_router(cook.router, prefix=settings.api_prefix)
    app.include_router(users.router, prefix=settings.api_prefix)

    @app.get("/")
    def root():
        return {"ok": True, "name": settings.app_name}

    return app


app = create_app()
