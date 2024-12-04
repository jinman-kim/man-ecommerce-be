# api/v1/endpoints/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.user import UserCreate, UserLogin, Token, UserDelete
from app.services.auth import create_user, login_user, delete_user
from app.utils.security import get_current_user

router = APIRouter()

@router.post("/user/signup", status_code=status.HTTP_201_CREATED)
async def signup(user: UserCreate):
    return await create_user(user)

@router.delete("/user/delete", status_code=status.HTTP_200_OK)
async def delete_user_endpoint(user: UserDelete):
    return await delete_user(user)

@router.post("/user/login", response_model=Token)
async def login(user: UserLogin):
    return await login_user(user)

@router.get("/protected")
async def protected_route(current_user: str = Depends(get_current_user)):
    return {"message": f"Hello, {current_user}"}
