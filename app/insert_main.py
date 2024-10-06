import os
from dotenv import load_dotenv
from elasticsearch import Elasticsearch, NotFoundError, helpers
import pandas as pd
from datetime import datetime, timedelta
# .env 파일에서 환경 변수 로드
load_dotenv()

# Elasticsearch 연결 설정
es_host = os.getenv('ELASTICSEARCH_HOST', 'http://localhost:9200')  # Changed default value
es = Elasticsearch([es_host], verify_certs=False)

def check_es_connection():
    """Elasticsearch 연결을 확인하는 함수"""
    if es.ping():
        print("Elasticsearch에 성공적으로 연결되었습니다.")
        return True
    else:
        print("Elasticsearch 연결에 실패했습니다.")
        return False

def create_index_if_not_exists(index_name):
    """인덱스가 없으면 기본 설정으로 생성하는 함수"""
    if not es.indices.exists(index=index_name):
        # 기본 설정
        settings = {
            "index": {
                "number_of_shards": 1,
                "number_of_replicas": 1
            }
        }
        mappings = {
            "properties": {
                "img_src": {"type": "text"},  # img src 필드 추가
                "category": {"type": "text"},
                "subject": {"type": "text"},  # subject 필드 추가
                "price": {"type": "integer"},
                "date": {"type": "date"},
                "location": {"type": "text"},
                "link": {"type": "text"},
                "status": {"type": "text"}
            }
        }
        
        # 인덱스 생성
        es.indices.create(index=index_name, body={
            "settings": settings,
            "mappings": mappings
        })
        
        print(f"인덱스 '{index_name}'가 생성되었습니다.")
    else:
        print(f"인덱스 '{index_name}'가 이미 존재합니다.")

def insert_data(index_name):
    df = pd.read_excel('./bunjang.xlsx')
    
    def generate_actions():
        for index, row in df.iterrows():
            try:
                doc = {
                    "img_src": str(row['src']),
                    "category": str(row['category']),
                    "subject": str(row['제목']),
                    "subject_suggest": str(row['제목']),
                    "price": int(row['price']) if pd.notna(row['price']) else 0,
                    "date": parse_date(str(row['등록일시'])),
                    "location": str(row['위치']) if pd.notna(row['위치']) else "",
                    "link": str(row['링크']) if pd.notna(row['링크']) else "",
                    "status": str(row['상태']) if pd.notna(row['상태']) else ""
                }
                
                # None 값 제거
                doc = {k: v for k, v in doc.items() if v is not None}
                
                yield {
                    "_index": index_name,
                    "_source": doc
                }
            except Exception as e:
                print(f"Error processing document {index}: {e}")
                print(f"Problematic row: {row}")

    try:
        # bulk 작업 실행
        success, failed = helpers.bulk(es, generate_actions(), stats_only=True)
        print(f"Successfully indexed {success} documents")
        if failed:
            print(f"Failed to index {failed} documents")
    except Exception as e:
        print(f"Error during bulk indexing: {e}")

    print("Indexing completed.")

def parse_date(date_str):
    try:
        if '일 전' in date_str:
            days_ago = int(date_str.replace('일 전', '').strip())
            return (datetime.now() - timedelta(days=days_ago)).strftime('%Y-%m-%d')
        elif '시간 전' in date_str:
            hours_ago = int(date_str.replace('시간 전', '').strip())
            return (datetime.now() - timedelta(hours=hours_ago)).strftime('%Y-%m-%d')
        elif '분 전' in date_str:
            minutes_ago = int(date_str.replace('분 전', '').strip())
            return (datetime.now() - timedelta(minutes=minutes_ago)).strftime('%Y-%m-%d')
        else:
            # 다른 날짜 형식에 대한 처리를 추가할 수 있습니다.
            return date_str
    except ValueError:
        print(f"날짜 파싱 오류: {date_str}")
        return None

def delete_index(es, index_name):
    """
    주어진 인덱스와 관련된 정책, 템플릿, 인덱스를 삭제하는 함수
    """
    # 1. 인덱스 삭제
    try:
        es.indices.delete(index=index_name)
        print(f"인덱스 '{index_name}'가 삭제되었습니다.")
    except NotFoundError:
        print(f"인덱스 '{index_name}'를 찾을 수 없습니다.")

    # 2. 인덱스 템플릿 삭제
    try:
        es.indices.delete_template(name=f"{index_name}_template")
        print(f"템플릿 '{index_name}_template'가 삭제되었습니다.")
    except NotFoundError:
        print(f"템플릿 '{index_name}_template'를 찾을 수 없습니다.")

    print(f"'{index_name}'와 관련된 모든 요소의 삭제 작업이 완료되었습니다.")

# 사용 예시
if __name__ == "__main__":
    # Elasticsearch 연결 설정
    es_host = os.getenv('ELASTICSEARCH_HOST', 'http://localhost:9200')
    es = Elasticsearch([es_host], verify_certs=False)
    index_name = "items"
    # 인덱스 삭제
    
    # delete_index(es, "items")
    
    # 새 인덱스 생성
    create_index_if_not_exists(index_name)
    
    # 데이터 삽입
    insert_data(index_name)
