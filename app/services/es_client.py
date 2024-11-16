# es_client.py

from elasticsearch import Elasticsearch
import logging

logger = logging.getLogger(__name__)

def get_elasticsearch_client(host: str = "localhost", port: int = 9200) -> Elasticsearch:
    es = Elasticsearch([{"host": host, "port": port}])
    if not es.ping():
        logger.error("Elasticsearch에 연결할 수 없습니다.")
        raise ConnectionError("Elasticsearch에 연결할 수 없습니다.")
    logger.info("Elasticsearch 클라이언트 초기화 완료")
    return es
