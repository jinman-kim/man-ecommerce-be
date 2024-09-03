from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.session import get_db
from schema import schemas
from services.test_service import TestService

router = APIRouter()

@router.get("/{user_id}", response_model=schemas.User)
def some_function(db: Session = Depends(get_db)):
    test_service = TestService(db)
    
    # 아이템 생성
    new_item = schemas.ItemCreate(title="New Item", description="Item Description")
    created_item = test_service.create_item(item_in=new_item, user_id=1)
    print(f"Created Item: {created_item}")
    
    # 아이템 조회
    items = test_service.get_items(skip=0, limit=10)
    print(f"Items: {items}")
