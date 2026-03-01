# app/core/auth_endpoints.py
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel

from app.core.auth import authenticate_user, create_access_token, get_current_user
from app.prime.memory.store import get_recent_context

router = APIRouter(prefix="/auth", tags=["auth"])


class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user_id: str
    display_name: str
    recent_turns: int


@router.post("/login", response_model=LoginResponse)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = create_access_token({"sub": user["user_id"]})
    recent = get_recent_context(user_id=user["user_id"], limit=10)

    return LoginResponse(
        access_token=token,
        token_type="bearer",
        user_id=user["user_id"],
        display_name=user["display_name"],
        recent_turns=len(recent),
    )


@router.get("/me")
async def get_me(current_user: dict = Depends(get_current_user)):
    recent = get_recent_context(user_id=current_user["user_id"], limit=10)
    return {
        "user_id": current_user["user_id"],
        "display_name": current_user["display_name"],
        "recent_turns": len(recent),
    }
