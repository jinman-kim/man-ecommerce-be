from sqlalchemy.orm import Session
from app import models
from app.schemas import schemas

class TestService:
    def __init__(self, db: Session):
        self.db = db

    def create_item(self, item_in: schemas.ItemCreate, user_id: int):
        item = models.Item(**item_in.dict(), owner_id=user_id)
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def get_items(self, skip: int = 0, limit: int = 10):
        return self.db.query(models.Item).offset(skip).limit(limit).all()