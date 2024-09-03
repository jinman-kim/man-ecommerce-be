from datetime import datetime
from elasticsearch import Elasticsearch

class EsService:
    def __init__(self, host: str = "http://localhost:9200"):
        self.host = host
        self.client = self._create_client()
    
    def _create_client(self) -> Elasticsearch:
        """Elasticsearch 클라이언트를 생성하고 반환합니다."""
        client = Elasticsearch(self.host)
        print(f"Connected to Elasticsearch at {self.host}")
        return client

    def create_index(self):
        """현재 날짜를 기반으로 인덱스를 생성합니다."""
        index_name = f"jinman-{datetime.now().strftime('%Y%m%d')}"
        
        if not self.client.indices.exists(index=index_name):
            self.client.indices.create(index=index_name)
            print(f"Index '{index_name}' created successfully.")
        else:
            print(f"Index '{index_name}' already exists.")

# EsService 클래스를 사용하여 Elasticsearch에 연결하고 인덱스 생성
if __name__ == "__main__":
    es_service = EsService()
    es_service.create_index()
