from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.database.models import User, Session as DBSession
from app.schemas.auth import UserCreate, UserLogin
from app.services.auth_service import (
    hash_password,
    verify_password
)
from app.services.security import (
    create_access_token,
    create_refresh_token,
    decode_refresh_token
)

from datetime import datetime, timezone

from app.services.security import (
    create_access_token,
    create_refresh_token,
    decode_refresh_token
)

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.post("/register")
def register_user(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    existing_user = (
        db.query(User)
        .filter(User.username == user_data.username)
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Username already exists"
        )

    hashed_password = hash_password(user_data.password)

    new_user = User(
    username=user_data.username,
    password_hash=hashed_password,
    role="signer"
)

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "message": "User registered successfully",
        "user": {
            "id": new_user.id,
            "username": new_user.username,
            "role": new_user.role
        }
    }


@router.post("/login")
def login_user(
    login_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = (
        db.query(User)
        .filter(User.username == login_data.username)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )

    if not verify_password(
        login_data.password,
        user.password_hash
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )

    access_token = create_access_token(
        user_id=user.id,
        username=user.username,
        role=user.role
    )

    refresh_token, token_id, refresh_expiry = (
        create_refresh_token(user.id)
    )

    new_session = DBSession(
        user_id=user.id,
        token_id=token_id,
        expires_at=refresh_expiry
    )

    db.add(new_session)
    db.commit()

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }
    
@router.post("/refresh")
def refresh_access_token(
    refresh_token: str,
    db: Session = Depends(get_db)
):
    payload = decode_refresh_token(refresh_token)

    if payload is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired refresh token"
        )

    token_id = payload.get("jti")
    user_id = payload.get("sub")

    session = (
        db.query(DBSession)
        .filter(DBSession.token_id == token_id)
        .first()
    )

    if session is None:
        raise HTTPException(
            status_code=401,
            detail="Session not found"
        )

    if session.revoked_at is not None:
        raise HTTPException(
            status_code=401,
            detail="Refresh token has been revoked"
        )

    if session.expires_at <= datetime.now(timezone.utc):
        raise HTTPException(
            status_code=401,
            detail="Refresh token has expired"
        )

    user = (
        db.query(User)
        .filter(User.id == int(user_id))
        .first()
    )

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="User not found"
        )

    new_access_token = create_access_token(
        user_id=user.id,
        username=user.username,
        role=user.role
    )

    return {
        "access_token": new_access_token,
        "token_type": "bearer"
    }
    
@router.post("/logout")
def logout_user(
    refresh_token: str,
    db: Session = Depends(get_db)
):
    payload = decode_refresh_token(refresh_token)

    if payload is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid refresh token"
        )

    token_id = payload.get("jti")

    session = (
        db.query(DBSession)
        .filter(DBSession.token_id == token_id)
        .first()
    )

    if session is None:
        raise HTTPException(
            status_code=404,
            detail="Session not found"
        )

    if session.revoked_at is not None:
        return {
            "message": "Session already revoked"
        }

    session.revoked_at = datetime.now(timezone.utc)

    db.commit()

    return {
        "message": "Logged out successfully"
    }