# app/services/crawl_service.py

import os
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup
from typing import List, Dict
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
    
    def crawl_item(self, items_options: List[List[str]]) -> List[Dict]:
        """
        요청에 따라 번개장터에서 아이템을 크롤링합니다.

        Args:
            items_options (List[List[str]]): 각 아이템의 옵션 리스트 [category, min_price, max_price, page_limit]

        Returns:
            List[Dict]: 크롤링된 데이터 리스트
        """
        if not self.browser:
            raise Exception("Selenium WebDriver가 초기화되지 않았습니다. 먼저 init_selenium을 호출하세요.")

        Category = []
        Subject = []
        Price = []
        Date = []
        Location = []
        Link = []
        Img_src = []
        Status = []

        for itemname in items_options:
            category, min_price, max_price, page_limit = itemname
            page = 1

            while True:
                if page > int(page_limit):
                    break

                # 가격 범위에 따른 검색 URL 생성
                url = f"https://m.bunjang.co.kr/search/products?order=price_asc&page={page}&q={category}"
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
                        # 0: 사진, 1: 이름, 가격, 시간, 2: 주소
                        img_tag = children[0].find('img')
                        Img_src.append(img_tag['src'] if img_tag else 'None')
                        status = '판매중'
                        for img in children[0].find_all('img'):
                            if img.get('alt') == '판매 완료':
                                status = '판매완료'
                                break
                        Status.append(status)

                        info = children[1].get_text(separator=';;;').split(';;;')
                        location = children[2].get_text()

                        Category.append(category)
                        Subject.append(info[0] if len(info) > 0 else 'None')
                        Price.append(info[1] if len(info) > 1 else 'None')
                        Date.append(info[2] if len(info) > 2 else 'None')
                        Location.append(location if location else 'None')
                        Link.append(f"https://m.bunjang.co.kr{aTag.get('href', '')}")
                    except Exception as e:
                        logger.error(f"데이터 추출 오류: {e}")
                        Category.append(category)
                        Subject.append('None')
                        Price.append('None')
                        Date.append('None')
                        Location.append('None')
                        Link.append('None')
                        Img_src.append('None')
                        Status.append('None')
                        continue

                page += 1

        # 데이터프레임 생성 및 전처리
        Datas = {
            "category": Category,
            "title": Subject,  # "제목"에서 변경
            "price": Price,
            "registration_date": Date,  # "등록일시"에서 변경
            "location": Location,  # "위치"에서 변경
            "link": Link,
            "src": Img_src,
            "status": Status  # "상태"에서 변경
        }

        df = pd.DataFrame(Datas)
        df.drop_duplicates(subset=['src'], inplace=True)
        df = df[df['status'] != '판매완료']
        df = df[df['price'] != '연락요망']
        df['price'] = df['price'].str.replace(';', '').str.replace(',', '').astype(int)

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

        # 가격 필터 함수 (필요에 맞게 수정)
        def price_filter(df, _info):
            category, min_price, max_price, _ = _info
            df_filtered = df[
                (df['category'] == category) &
                (df['price'].between(int(min_price), int(max_price)))
            ].reset_index(drop=True)
            return df_filtered.sort_values('price')

        df_concat = pd.concat([price_filter(df, opt) for opt in items_options])

        # 결과를 딕셔너리 리스트로 반환
        result = df_concat.to_dict(orient='records')

        return result

    def save_item(self, data: List[Dict], index_name: str = "bunjang"):
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

        # 데이터 삽입
        actions = [
            {
                "_index": index_name,
                "_source": item
            }
            for item in data
        ]

        helpers.bulk(self.es, actions)
        logger.info(f"데이터가 Elasticsearch 인덱스 '{index_name}'에 저장되었습니다.")
