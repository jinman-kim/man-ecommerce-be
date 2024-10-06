from elasticsearch import Elasticsearch
import os

class SearchService:
    def __init__(self):
        self.es = Elasticsearch([os.environ.get('ELASTICSEARCH_URL', 'http://localhost:9200')])

    async def search_items(self, page: int, page_size: int, search_query: str = None):
        body = {
            "from": (page - 1) * page_size,
            "size": page_size,
            "query": {
                "match_all": {}
            } if not search_query else {
                "multi_match": {
                    "query": search_query,
                    "fields": ["제목", "위치"]
                }
            }
        }

        result = self.es.search(index="products", body=body)
        return [hit['_source'] for hit in result['hits']['hits']]