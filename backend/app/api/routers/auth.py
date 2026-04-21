from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.config import settings
from app.core.database import get_db
from app.core.security import (
    create_access_token,
    create_reset_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.models.cooking import PasswordResetToken
from app.models.user import User
from app.schemas.auth import (
    LoginIn,
    PasswordResetConfirmIn,
    PasswordResetRequestIn,
    RegisterIn,
    UserOut,
)

router = APIRouter(prefix="/auth", tags=["auth"])


def _set_auth_cookie(response: Response, token: str):
    response.set_cookie(
        key=settings.auth_cookie_name,
        value=token,
        httponly=True,
        secure=settings.auth_cookie_secure,
        samesite=settings.auth_cookie_samesite,
        max_age=settings.access_token_expire_minutes * 60,
        path="/",
    )


@router.post("/register", response_model=UserOut, status_code=201)
def register(data: RegisterIn, response: Response, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == data.email.lower()).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    user = User(email=data.email.lower(), password_hash=hash_password(data.password))
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token(user.id)
    _set_auth_cookie(response, token)

    return UserOut(id=user.id, email=user.email, profile_constraints=user.profile_constraints)


@router.post("/login", response_model=UserOut)
def login(data: LoginIn, response: Response, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email.lower()).first()
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token(user.id)
    _set_auth_cookie(response, token)

    return UserOut(id=user.id, email=user.email, profile_constraints=user.profile_constraints)


@router.post("/logout", status_code=204)
def logout(response: Response):
    response.delete_cookie(key=settings.auth_cookie_name, path="/")
    return Response(status_code=204)


@router.get("/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)):
    return UserOut(id=user.id, email=user.email, profile_constraints=user.profile_constraints)


@router.post("/password-reset/request")
def request_password_reset(data: PasswordResetRequestIn, db: Session = Depends(get_db)):
    """Demo flow: returns reset token in response.

    In production: send by email.
    """
    user = db.query(User).filter(User.email == data.email.lower()).first()
    if not user:
        # Do not leak whether email exists
        return {"ok": True}

    token, jti, expires_at = create_reset_token(user.id)
    record = PasswordResetToken(user_id=user.id, token_jti=jti, expires_at=expires_at)
    db.add(record)
    db.commit()

    return {
        "ok": True,
        "token": token,
        "note": "DEMO: token returned in API response. In prod you would email it.",
        "expires_at": expires_at,
    }


@router.post("/password-reset/confirm")
def confirm_password_reset(data: PasswordResetConfirmIn, db: Session = Depends(get_db)):
    try:
        payload = decode_token(data.token)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid or expired token")
    if payload.purpose != "reset" or not payload.jti:
        raise HTTPException(status_code=400, detail="Invalid token")

    record = db.query(PasswordResetToken).filter(PasswordResetToken.token_jti == payload.jti).first()
    if not record or record.is_used:
        raise HTTPException(status_code=400, detail="Token already used")


    user = db.get(User, int(payload.sub))
    if not user:
        raise HTTPException(status_code=400, detail="User not found")

    user.password_hash = hash_password(data.new_password)
    record.is_used = True
    db.add(user)
    db.add(record)
    db.commit()

    return {"ok": True}
