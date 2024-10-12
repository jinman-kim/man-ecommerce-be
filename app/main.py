from fastapi import FastAPI
from api.v1.api import api_router
from core.config import settings
from db.init_db import init_db
from db.session import engine
from services.es_service import EsService
from services.kafka_service import KafkaService

app = FastAPI(title=settings.PROJECT_NAME, openapi_url=f"{settings.API_V1_STR}/openapi.json")

@app.on_event("startup")
def on_startup():
    init_db(engine)
    # Elasticsearch 서비스 초기화 및 인덱스 생성
    try:
        es_service = EsService()  # EsService 인스턴스 생성
        es_service.create_index()  # 인덱스 생성
    except Exception as e:
        print(f"Elasticsearch 서비스 초기화 중 오류 발생: {e}")

    # Kafka 서비스 초기화 및 토픽 생성
    try:
        kafka_service = KafkaService()  # KafkaService 인스턴스 생성
        kafka_service.create_topic("initial-topic")  # 초기 토픽 생성
    except Exception as e:
        print(f"Kafka 서비스 초기화 중 오류 발생: {e}")
        
app.include_router(api_router, prefix=settings.API_V1_STR)
