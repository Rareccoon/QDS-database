from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer

from app.services.security import decode_access_token


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/login"
)


def get_current_user(
    token: str = Depends(oauth2_scheme)
):
    payload = decode_access_token(token)

    if payload is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )

    return payload


def require_role(required_role: str):
    def role_checker(
        current_user: dict = Depends(get_current_user)
    ):
        user_role = current_user.get("role")

        if user_role != required_role:
            raise HTTPException(
                status_code=403,
                detail="Insufficient permissions"
            )

        return current_user

    return role_checker