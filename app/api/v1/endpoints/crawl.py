# app/api/v1/endpoints/crawl.py

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import List
from app.services.crawl_service import CrawlService
from app.dependencies import get_crawl_service  # 의존성 주입 함수 import
import logging

router = APIRouter()

logger = logging.getLogger('Crawler')

class ItemOption(BaseModel):
    category: str = Field(..., example="프라다")
    min_price: int = Field(..., example=250000)
    max_price: int = Field(..., example=1000000)
    page_limit: int = Field(..., example=3)

class CrawlRequest(BaseModel):
    items_options: List[ItemOption]

@router.post("/", summary="Bunjang 크롤링 실행")
def crawl_endpoint(request: CrawlRequest, crawl_service: CrawlService = Depends(get_crawl_service)):
    items_options = [
        {
            "category": item.category,
            "min_price": item.min_price,
            "max_price": item.max_price,
            "page_limit": item.page_limit
        }
        for item in request.items_options
    ]
    
    try:
        result = crawl_service.run_scraper(items_options=items_options, num_workers=8)
        status = crawl_service.save_item(result, index_name='items')
        return status
    except Exception as e:
        logger.error(f"Crawl 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))
        