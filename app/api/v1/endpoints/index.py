from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import models
from schema import schemas
from db.session import get_db
from services.item_service import create_item, get_items

router = APIRouter()

@router.post("/index_item", response_model=schemas.Item)
def index_item(item_in: schemas.ItemCreate, db: Session = Depends(get_db)):
    item = create_item(db=db, item_in=item_in)
    return item

@router.get("/index_items", response_model=list[schemas.Item])
def index_items(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    items = get_items(db=db, skip=skip, limit=limit)
    return items
