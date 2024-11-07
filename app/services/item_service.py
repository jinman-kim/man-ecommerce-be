from sqlalchemy.orm import Session
from app import models 
from app.schema import schemas

def create_item(db: Session, item_in: schemas.ItemCreate, user_id: int):
    item = models.Item(**item_in.dict(), owner_id=user_id)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item

def get_items(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.Item).offset(skip).limit(limit).all()
