# tests/test_search.py

import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock
from main import app  # FastAPI 애플리케이션 인스턴스
from app.schema.search import SearchRequest, SearchResponse, SearchResponseItem

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def mock_search_service(mocker):
    # SearchService의 search_items 메서드를 모킹합니다
    mock_service = MagicMock()
    mocker.patch('app.routers.search.get_search_service', return_value=mock_service)
    return mock_service

def test_search_items_success(client, mock_search_service):
    # 테스트 입력 데이터
    search_request = {
        "query": "테스트 아이템",
        "min_price": 10000,
        "max_price": 50000,
        "sort": "price",
        "order": "asc",
        "size": 10,
        "page": 1
    }

    # 예상되는 검색 결과
    search_response = SearchResponse(
        total=1,
        page=1,
        size=10,
        last_sort=None,
        results=[
            SearchResponseItem(
                category="전자제품",
                제목="테스트 아이템",
                price=25000,
                등록일시="2023-10-31T12:34:56",
                위치="서울",
                링크="https://example.com/item/1",
                src="https://example.com/item/1/image.jpg",
                상태="판매중"
            )
        ]
    )

    # 모킹된 search_service의 반환값 설정
    mock_search_service.search_items.return_value = search_response.dict()

    # API 호출
    response = client.post("/search/", json=search_request)

    # 응답 검증
    assert response.status_code == 200
    assert response.json() == search_response.dict()

    # search_items가 올바른 인자로 호출되었는지 확인
    mock_search_service.search_items.assert_called_once()
    args, kwargs = mock_search_service.search_items.call_args
    assert args[0] == SearchRequest(**search_request)

def test_search_items_failure(client, mock_search_service):
    # 테스트 입력 데이터
    search_request = {
        "query": "테스트 아이템",
        "min_price": 10000,
        "max_price": 50000,
        "sort": "price",
        "order": "asc",
        "size": 10,
        "page": 1
    }

    # 모킹된 search_service가 예외를 발생하도록 설정
    mock_search_service.search_items.side_effect = Exception("Elasticsearch 오류")

    # API 호출
    response = client.post("/search/", json=search_request)

    # 응답 검증
    assert response.status_code == 500
    assert response.json() == {"detail": "검색 중 오류가 발생했습니다."}

    # search_items가 올바른 인자로 호출되었는지 확인
    mock_search_service.search_items.assert_called_once()
    args, kwargs = mock_search_service.search_items.call_args
    assert args[0] == SearchRequest(**search_request)
