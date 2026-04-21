import base64
import hashlib
import hmac
import os
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from jose import jwt

from app.core.config import settings


def hash_password(password: str) -> str:
    """PBKDF2-HMAC-SHA256 with random salt.

    Stored format: pbkdf2_sha256$<iterations>$<salt>$<hash>
    """
    salt = base64.urlsafe_b64encode(os.urandom(16)).decode("utf-8").rstrip("=")
    dk = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        settings.password_hash_iterations,
    )
    hashed = base64.urlsafe_b64encode(dk).decode("utf-8").rstrip("=")
    return f"pbkdf2_sha256${settings.password_hash_iterations}${salt}${hashed}"


def verify_password(password: str, stored: str) -> bool:
    try:
        scheme, iterations_s, salt, hashed = stored.split("$", 3)
        if scheme != "pbkdf2_sha256":
            return False
        iterations = int(iterations_s)
        dk = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt.encode("utf-8"),
            iterations,
        )
        computed = base64.urlsafe_b64encode(dk).decode("utf-8").rstrip("=")
        return hmac.compare_digest(computed, hashed)
    except Exception:
        return False


@dataclass
class TokenPayload:
    sub: str
    exp: int
    purpose: str = "access"
    jti: str | None = None


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def create_access_token(user_id: int) -> str:
    expire = _now_utc() + timedelta(minutes=settings.access_token_expire_minutes)
    payload = {
        "sub": str(user_id),
        "exp": int(expire.timestamp()),
        "purpose": "access",
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def create_reset_token(user_id: int, minutes: int = 20) -> tuple[str, str, datetime]:
    """Returns (token, jti, expires_at)."""
    expire_dt = _now_utc() + timedelta(minutes=minutes)
    jti = base64.urlsafe_b64encode(os.urandom(24)).decode("utf-8").rstrip("=")
    payload = {
        "sub": str(user_id),
        "exp": int(expire_dt.timestamp()),
        "purpose": "reset",
        "jti": jti,
    }
    token = jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
    return token, jti, expire_dt


def decode_token(token: str) -> TokenPayload:
    data = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
    return TokenPayload(
        sub=data["sub"],
        exp=data["exp"],
        purpose=data.get("purpose", "access"),
        jti=data.get("jti"),
    )
