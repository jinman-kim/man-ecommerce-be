from sqlalchemy.orm import Session
from app import models
from app.schemas import schemas
from app.core.security import get_password_hash

def create_user(db: Session, user_in: schemas.UserCreate):
    hashed_password = get_password_hash(user_in.password)
    user = models.User(email=user_in.email, hashed_password=hashed_password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()
