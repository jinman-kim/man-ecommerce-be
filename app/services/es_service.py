import json
from datetime import datetime
import logging
import os
from elasticsearch import Elasticsearch, helpers
logger = logging.getLogger(__name__)


class EsService:
    def __init__(self, host: str = "http://localhost:9200", mapping_path: str = "app/config/items_mapping.json"):
        self.host = host
        self.mapping_path = mapping_path
        self.client = self._create_client()
    
    def _create_client(self) -> Elasticsearch:
        """Elasticsearch 클라이언트를 생성하고 반환합니다."""
        client = Elasticsearch(self.host)
        print(f"Connected to Elasticsearch at {self.host}")
        return client

    def create_index(self, index_name: str = "items"):
        """
        `items_mapping.json` 파일을 기반으로 Elasticsearch 인덱스를 생성합니다.
        인덱스가 이미 존재하면 생성을 건너뜁니다.
        
        Args:
            index_name (str): 생성할 인덱스 이름
        """
        # 인덱스가 이미 존재하는지 확인
        if self.client.indices.exists(index=index_name):
            logger.info(f"Index '{index_name}' already exists.")
            return

        # 매핑 파일 경로 확인
        if not os.path.exists(self.mapping_path):
            logger.error(f"매핑 파일을 찾을 수 없습니다: {self.mapping_path}")
            raise FileNotFoundError(f"매핑 파일을 찾을 수 없습니다: {self.mapping_path}")

        # 매핑 파일 읽기
        try:
            with open(self.mapping_path, 'r', encoding='utf-8') as file:
                mapping = json.load(file)
                logger.info(f"매핑 파일 '{self.mapping_path}' 로드 완료.")
        except Exception as e:
            logger.error(f"매핑 파일 로드 중 오류 발생: {e}")
            raise e

        # 인덱스 생성
        try:
            self.client.indices.create(index=index_name, body=mapping)
            logger.info(f"Index '{index_name}' created successfully with provided mapping.")
        except Exception as e:
            logger.error(f"인덱스 생성 중 오류 발생: {e}")
            raise e

# EsService 클래스를 사용하여 Elasticsearch에 연결하고 인덱스 생성
if __name__ == "__main__":
    es_service = EsService()
    es_service.create_index()
