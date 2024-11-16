from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import models
from app.schema import schemas
from app.db.session import get_db
from app.services.user_service import create_user, get_user

router = APIRouter()

@router.post("/", response_model=schemas.User)
def create_new_user(user_in: schemas.UserCreate, db: Session = Depends(get_db)):
    user = create_user(db=db, user_in=user_in)
    return user

@router.get("/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    user = get_user(db=db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
