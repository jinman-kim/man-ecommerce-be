from app.db.database import database
from app.utils.security import hash_password, verify_password, create_access_token
from app.schemas.user import UserCreate, UserDelete, UserLogin
from app.sql import user_queries  # 쿼리 모듈 임포트
from typing import Optional
from fastapi import HTTPException, status

async def get_user_by_username(username: str) -> Optional[dict]:
    query = user_queries.GET_USER_BY_USERNAME
    user = await database.pool.fetchrow(query, username)
    return user

async def create_user(user: UserCreate):
    existing_user = await get_user_by_username(user.username)
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    hashed_pwd = hash_password(user.password)
    query = user_queries.CREATE_USER
    await database.pool.execute(query, user.username, hashed_pwd)
    return {"message": "User created successfully"}

async def delete_user(user: UserDelete):
    existing_user = await get_user_by_username(user.username)
    
    if not existing_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.password != user.double_check_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")
    
    if not verify_password(user.password, existing_user['hashed_password']):
        raise HTTPException(status_code=401, detail="Incorrect password")
    
    query = user_queries.DELETE_USER
    await database.pool.execute(query, existing_user['id'])
    return {"message": "User deleted successfully"}


async def authenticate_user(username: str, password: str):
    user = await get_user_by_username(username)
    if not user:
        return None
    if not verify_password(password, user['hashed_password']):
        return None
    return user

async def login_user(user: UserLogin):
    authenticated_user = await authenticate_user(user.username, user.password)
    if not authenticated_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": authenticated_user['username']})
    return {"access_token": access_token, "token_type": "bearer"}
