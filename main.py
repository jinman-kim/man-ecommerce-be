# app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import api_router
from app.core.config import settings
from app.db.init_db import init_db
from app.db.session import engine
from app.db.database import database

from app.services.es_service import EsService
from app.services.kafka_service import KafkaService
from app.services.crawl_service import CrawlService
from app.services.service_container import service_container
import logging

app = FastAPI(title=settings.PROJECT_NAME, openapi_url=f"{settings.API_V1_STR}/openapi.json")

app = FastAPI()

# CORS 허용할 도메인 리스트
origins = [
    "http://localhost:3000",  # React 개발 서버 주소
    # 다른 도메인이 필요하다면 추가
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # 허용할 도메인
    allow_credentials=True,
    allow_methods=["*"],    # 허용할 HTTP 메서드
    allow_headers=["*"],    # 허용할 HTTP 헤더
)

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.on_event("startup")
async def on_startup():
    await database.connect()
    
    # Elasticsearch 서비스 초기화 및 인덱스 생성
    try:
        es_service = EsService()
        es_service.create_index()
        logger.info("Elasticsearch 인덱스 생성 완료")
    except Exception as e:
        logger.error(f"Elasticsearch 서비스 초기화 중 오류 발생: {e}")
    
    # Kafka 서비스 초기화 및 토픽 생성
    try:
        kafka_service = KafkaService()
        kafka_service.create_topic("initial-topic")
        logger.info("Kafka 토픽 생성 완료")
    except Exception as e:
        logger.error(f"Kafka 서비스 초기화 중 오류 발생: {e}")
    
    # Selenium 서비스 초기화
    try:
        service_container.crawl_service = CrawlService()
        service_container.crawl_service.init_selenium()
        logger.info("CrawlService 초기화 완료")
    except Exception as e:
        logger.error(f"Selenium 구동 실패: {e}")

@app.on_event("shutdown")
def on_shutdown():
    if service_container.crawl_service and service_container.crawl_service.browser:
        service_container.crawl_service.browser.quit()
        logger.info("Selenium WebDriver 종료 완료")

app.include_router(api_router, prefix=settings.API_V1_STR)

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(
        'main:app',
        host="127.0.0.1",
        port=8003,
        reload=True,
    )
