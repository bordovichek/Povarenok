from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_ignore_empty=True)

    app_name: str = "Smart Cookbook"
    api_prefix: str = "/api"

    # Database
    database_url: str = "postgresql+psycopg2://postgres:postgres@db:5432/smart_cookbook"

    # Security (JWT in HttpOnly cookie)
    jwt_secret_key: str = "CHANGE_ME_IN_PROD"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24 * 7  # 7 days

    auth_cookie_name: str = "sc_access"
    auth_cookie_secure: bool = False  # set True behind HTTPS
    auth_cookie_samesite: str = "lax"

    # Password hashing (PBKDF2-HMAC-SHA256)
    password_hash_iterations: int = 310_000

    # CORS (comma-separated)
    cors_origins: str = "http://localhost:8080,http://localhost:3000"

    # Optional LLM integration (if you want real text generation)
    openai_api_key: str | None = None


settings = Settings()
