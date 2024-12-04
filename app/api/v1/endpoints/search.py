# routers/search.py

from fastapi import APIRouter, HTTPException, Depends
from elasticsearch import Elasticsearch
from typing import Optional, List
from app.schemas.search import SearchRequest, SearchResponse
from app.services.search_service import SearchService

router = APIRouter(
    tags=["Search"]
)

# Elasticsearch 클라이언트 초기화 함수 (es_client.py로 분리할 수도 있음)
def get_elasticsearch_client(host: str = "http://localhost:9200") -> Elasticsearch:
    es = Elasticsearch(host)
    if not es.ping():
        raise HTTPException(status_code=500, detail="Elasticsearch에 연결할 수 없습니다.")
    return es

# SearchService 의존성 주입
def get_search_service(es: Elasticsearch = Depends(get_elasticsearch_client)) -> SearchService:
    return SearchService(es=es, index_name="items")

@router.post("/", response_model=SearchResponse)
def search_items(
    request: SearchRequest,
    search_service: SearchService = Depends(get_search_service)
):
    """
    Elasticsearch에서 '제목' 필드로 검색을 수행하는 엔드포인트입니다.
    """
    try:
        result = search_service.search_items(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail="검색 중 오류가 발생했습니다.")
