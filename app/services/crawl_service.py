# app/services/crawl_service.py

import os
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup
from typing import List, Dict, Any
import time
from elasticsearch import Elasticsearch, helpers
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CrawlService:
    def __init__(self, chromedriver_path: str=None, elasticsearch_url: str = "http://localhost:9200"):
        self.chromedriver_path = chromedriver_path
        self.elasticsearch_url = elasticsearch_url
        self.browser = None
        self.es = None

    def init_selenium(self):
        """Selenium WebDriver 초기화 및 bunjang.co.kr 접속"""
        self.options = webdriver.ChromeOptions()
        self.options.add_argument("headless")
        self.browser = webdriver.Chrome(options=self.options)
        self.browser.get('https://m.bunjang.co.kr/')
        logger.info("Selenium WebDriver 초기화 완료 및 bunjang.co.kr 접속")

    def get_browser(self):
        """브라우저 인스턴스를 반환합니다. 초기화되지 않았으면 초기화합니다."""
        if self.browser is None:
            self.init_selenium()
        return self.browser
    
    def run_scraper(self, items_options: List[List[str]], num_workers: int = 1) -> List[Dict]:
        """
        크롤러 실행 메서드. 기존의 crawl_item 메서드를 호출합니다.
        
        Args:
            items_options (List[List[str]]): 각 아이템의 옵션 리스트 [category, min_price, max_price, page_limit]
            num_workers (int): 병렬 작업 수 (현재는 단일 스레드로 동작)
        
        Returns:
            List[Dict]: 크롤링된 데이터 리스트
        """
        return self.crawl_item(items_options)
    
    def crawl_item(self, items_options: List[Dict[str, Any]]) -> List[Dict]:
        """
        요청에 따라 번개장터에서 아이템을 크롤링합니다.

        Args:
            items_options (List[Dict[str, Any]]): 각 아이템의 옵션 딕셔너리 리스트

        Returns:
            List[Dict]: 크롤링된 데이터 리스트
        """
        if not self.browser:
            raise Exception("Selenium WebDriver가 초기화되지 않았습니다. 먼저 init_selenium을 호출하세요.")

        # 데이터 수집 리스트 초기화
        Datas = {
            "category": [],
            "title": [],
            "price": [],
            "registration_date": [],
            "location": [],
            "link": [],
            "src": [],
            "status": []
        }


        for item_option in items_options:
            category = item_option["category"]
            min_price = int(item_option["min_price"])
            max_price = int(item_option["max_price"])
            page_limit = int(item_option["page_limit"])
            page = 1

            while page <= page_limit:
                url = f"https://m.bunjang.co.kr/search/products?order=date&page={page}&q={category}"
                self.browser.get(url)
                logger.info(f"크롤링 중: 카테고리={category}, 페이지={page}")
                time.sleep(3)  # 페이지 로딩 대기

                html = self.browser.page_source
                html_parser = BeautifulSoup(html, "html.parser")
                _list = html_parser.find_all(attrs={'alt': '상품 이미지'})

                if not _list:
                    break  # 더 이상 페이지가 없으면 종료

                for item in _list:
                    aTag = item.parent.parent
                    children = list(aTag.children)

                    try:
                        # 데이터 추출
                        img_tag = children[0].find('img')
                        src = img_tag['src'] if img_tag else 'None'
                        status = '판매중'
                        for img in children[0].find_all('img'):
                            if img.get('alt') == '판매 완료':
                                status = '판매완료'
                                break

                        info = children[1].get_text(separator=';;;').split(';;;')
                        location = children[2].get_text()

                        title = info[0] if len(info) > 0 else 'None'
                        price = info[1] if len(info) > 1 else 'None'
                        date = info[2] if len(info) > 2 else 'None'

                        # 데이터 수집
                        Datas["category"].append(category)
                        Datas["title"].append(title)
                        Datas["price"].append(price)
                        Datas["registration_date"].append(date)
                        Datas["location"].append(location if location else 'None')
                        Datas["link"].append(f"https://m.bunjang.co.kr{aTag.get('href', '')}")
                        Datas["src"].append(src)
                        Datas["status"].append(status)
                    except Exception as e:
                        logger.error(f"데이터 추출 오류: {e}")
                        # 누락된 데이터라도 기본값으로 추가
                        Datas["category"].append(category)
                        Datas["title"].append('None')
                        Datas["price"].append('None')
                        Datas["registration_date"].append('None')
                        Datas["location"].append('None')
                        Datas["link"].append('None')
                        Datas["src"].append('None')
                        Datas["status"].append('None')
                        continue
                page += 1


        df = pd.DataFrame(Datas)
        df.drop_duplicates(subset=['src'], inplace=True)
        df = df[df['status'] != '판매완료']
        df = df[df['price'] != '연락요망']

        try:
            df['price'] = df['price'].str.replace(';', '').str.replace(',', '').astype(int)
        except ValueError as ve:
            logger.error(f"가격 변환 오류: {ve}")
            df['price'] = pd.to_numeric(df['price'].str.replace(';', '').str.replace(',', ''), errors='coerce')

        # 날짜 변환 함수
        def date_shifter(df):
            def custom_convert(date_str):
                if '주' in date_str:
                    return f"{int(date_str.split('주')[0]) * 7}일 전"
                elif '달' in date_str:
                    return f"{int(date_str.split('달')[0]) * 30}일 전"
                else:
                    return date_str

            df['registration_date'] = df['registration_date'].apply(custom_convert)
            return df

        df = date_shifter(df)
        # 가격 필터 적용
        filtered_dfs = []
        for item_option in items_options:
            category = item_option["category"]
            min_price = int(item_option["min_price"])
            max_price = int(item_option["max_price"])

            df_filtered = df[
                (df['category'] == category) &
                (df['price'].between(min_price, max_price))
            ].reset_index(drop=True)

            filtered_dfs.append(df_filtered)

        df_concat = pd.concat(filtered_dfs, ignore_index=True)
        logger.info(f"필터링 및 정렬 후 데이터: {len(df_concat)}")

        # 결과를 딕셔너리 리스트로 반환
        result = df_concat.to_dict(orient='records')

        return result

    def save_item(self, data: List[Dict], index_name: str = "items"):
        """
        크롤링한 데이터를 Elasticsearch에 저장합니다.

        Args:
            data (List[Dict]): 저장할 데이터 리스트
            index_name (str): Elasticsearch 인덱스 이름
        """
        if not self.es:
            self.es = Elasticsearch([self.elasticsearch_url])
            if not self.es.ping():
                raise ValueError("Elasticsearch에 연결할 수 없습니다.")

        # 인덱스가 존재하지 않으면 생성
        if not self.es.indices.exists(index=index_name):
            self.es.indices.create(index=index_name)
            logger.info(f"Elasticsearch 인덱스 '{index_name}' 생성 완료")

        # 중복 데이터 검색을 위한 link와 src 리스트 생성
        links = [item['link'] for item in data]
        srcs = [item['src'] for item in data]
        # 중복 문서 검색 (link 또는 src가 일치하는 문서)
        search_query = {
            "query": {
                "bool": {
                    "should": [
                        {"terms": {"link": links}},
                        {"terms": {"src": srcs}}
                    ],
                    "minimum_should_match": 1
                }
            },
            "_source": False  # 소스 필드를 가져올 필요 없으므로 비활성화
        }

        try:
            response = self.es.search(index=index_name, body=search_query, size=10000)  # size는 최대 10000까지
            hits = response['hits']['hits']
            if hits:
                # 삭제할 문서 ID 리스트 생성
                delete_ids = [hit['_id'] for hit in hits]
                logger.info(f"삭제할 중복 문서 수: {len(delete_ids)}")

                # Bulk 삭제 요청 준비
                delete_actions = [
                    {
                        "_op_type": "delete",
                        "_index": index_name,
                        "_id": doc_id
                    }
                    for doc_id in delete_ids
                ]

                # Bulk 삭제 실행
                helpers.bulk(self.es, delete_actions)
                logger.info(f"중복 문서 삭제 완료: {len(delete_ids)}개")
            else:
                logger.info("삭제할 중복 문서가 없습니다.")

        except Exception as e:
            logger.error(f"중복 문서 검색 또는 삭제 중 오류 발생: {e}")
            return {"status": "error", "message": f"중복 문서 처리 중 오류 발생: {e}"}

    
        # 데이터 삽입
        actions = [
            {
                "_index": index_name,
                "_source": item
            }
            for item in data
        ]

        logger.info(f"물건 {len(actions)}개 저장 시도")

        helpers.bulk(self.es, actions)
        logger.info(f"데이터가 Elasticsearch 인덱스 '{index_name}'에 저장되었습니다.")
