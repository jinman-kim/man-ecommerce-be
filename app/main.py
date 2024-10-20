# app/main.py

from fastapi import FastAPI
from api.v1 import api_router
from core.config import settings
from db.init_db import init_db
from db.session import engine
from services.es_service import EsService
from services.kafka_service import KafkaService
from services.crawl_service import CrawlService
from services.service_container import service_container
import logging

app = FastAPI(title=settings.PROJECT_NAME, openapi_url=f"{settings.API_V1_STR}/openapi.json")

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.on_event("startup")
def on_startup():
    init_db(engine)
    
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
