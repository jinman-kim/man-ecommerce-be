# app/dependencies.py

from fastapi import Depends, HTTPException
from services.service_container import service_container
from services.crawl_service import CrawlService

def get_crawl_service() -> CrawlService:
    if not service_container.crawl_service:
        raise HTTPException(status_code=500, detail="CrawlService 인스턴스가 초기화되지 않았습니다.")
    return service_container.crawl_service
