# services/search_service.py

from typing import Optional, List, Dict
from elasticsearch import Elasticsearch
import logging
from app.schema.search import SearchRequest, SearchResponseItem

logger = logging.getLogger(__name__)

class SearchService:
    def __init__(self, es: Elasticsearch, index_name: str = "bunjang"):
        self.es = es
        self.index_name = index_name

    def search_items(self, request: SearchRequest) -> Dict:
        """
        Elasticsearch에서 '제목' 필드로 검색을 수행합니다.

        Args:
            request (SearchRequest): 검색 요청 데이터

        Returns:
            Dict: 검색 결과
        """
        try:
            # Elasticsearch 쿼리 구성
            es_query = {
                "bool": {
                    "must": {
                        "match": {
                            "category": {
                                "query": request.query,
                                "operator": "and"  # 정확한 매칭을 원할 경우 "and" 사용
                            }
                        }
                    },
                    "filter": []
                }
            }

            # 가격 범위 필터 추가
            if request.min_price is not None or request.max_price is not None:
                price_filter = {}
                if request.min_price is not None:
                    price_filter["gte"] = request.min_price
                if request.max_price is not None:
                    price_filter["lte"] = request.max_price
                es_query["bool"]["filter"].append({
                    "range": {
                        "price": price_filter
                    }
                })

            # 정렬 옵션 구성
            sort_option = {request.sort: {"order": request.order}}

            # Elasticsearch 검색 요청 본문 구성
            body = {
                "query": es_query,
                "sort": [sort_option],
                "size": request.size,
                "_source": ["category", "제목", "price", "등록일시", "위치", "링크", "src", "상태"]  # 필요한 필드만 로드
            }

            # 페이지네이션 설정
            if request.search_after:
                body["search_after"] = request.search_after
            else:
                # 페이지 번호 기반 페이지네이션 (from/size 사용)
                from_ = (request.page - 1) * request.size
                body["from"] = from_

            # Elasticsearch 검색 요청
            logger.info(f"es query : {body}")
            response = self.es.search(
                index=self.index_name,
                body=body
            )

            hits = response["hits"]["hits"]
            total = response["hits"]["total"]["value"]

            # 마지막 문서의 sort 값을 search_after로 전달
            last_sort = hits[-1]["sort"] if hits else None

            # 결과 포맷팅
            results = [SearchResponseItem(**hit["_source"]) for hit in hits]

            return {
                "total": total,
                "page": request.page if not request.search_after else None,
                "size": request.size,
                "last_sort": last_sort,
                "results": results
            }

        except Exception as e:
            logger.error(f"검색 실패: {e}")
            raise
