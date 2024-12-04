# schemas/search.py

from typing import Optional, List
from pydantic import BaseModel, Field, validator

class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, example="프라다", description="검색할 제목 키워드")
    min_price: Optional[int] = Field(None, ge=0, example=200000, description="최소 가격")
    max_price: Optional[int] = Field(None, ge=0, example=5000000, description="최대 가격")
    sort: Optional[str] = Field(
        "price",
        regex="^(price)$",  # '등록일시'를 제외하고 'price'만 허용
        description="정렬 기준 (price)"
    )
    order: Optional[str] = Field(
        "desc",
        regex="^(asc|desc)$",
        description="정렬 순서 (asc 또는 desc)"
    )
    page: Optional[int] = Field(1, ge=1, description="페이지 번호")
    size: int = Field(10, ge=1, le=100, description="페이지당 항목 수")
    search_after: Optional[List[int]] = Field(
        None,
        description="search_after 값 (sort 기준으로 전달)"
    )

    @validator('search_after', always=True)
    def check_search_after(cls, v, values):
        if v and ('page' in values and values['page'] != 1):
            raise ValueError("search_after는 페이지 1이 아닐 때만 사용 가능합니다.")
        return v

class SearchResponseItem(BaseModel):
    category: Optional[str]
    title: Optional[str]
    price: Optional[int]
    registration_date: Optional[str]
    location: Optional[str]
    link: Optional[str]
    src: Optional[str]
    status: Optional[str]

class SearchResponse(BaseModel):
    total: int
    page: Optional[int] = None  # search_after 사용 시 페이지 정보가 필요 없을 수 있음
    size: int
    last_sort: Optional[List[int]] = None  # search_after에 사용되는 sort 값
    results: List[SearchResponseItem]
