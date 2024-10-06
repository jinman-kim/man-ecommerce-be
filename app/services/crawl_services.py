from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup
import pandas as pd
from multiprocessing import Pool
import os
from itertools import chain


item_clothes = [
    ['크롬하츠 볼캡', 130000, 250000, 2],
    ['질샌더 반팔', 50000, 130000, 2],
    ['솔리드옴므 반팔', 50000, 90000, 3],
    ['우영미 반팔', 50000, 150000, 3],
    ['릭오웬스', 150000, 500000, 6],
    ['휴먼메이드 xxl', 40000, 100000, 3],
    ['휴먼메이드 xl', 40000, 100000, 3],
    ['갤러리디파트먼트', 100000, 400000, 3],
]

item_bottega = [
    ['보테가베네타', 150000, 500000, 11],
]

item_elec = [
    ['에어팟 맥스', 300000, 450000, 5],
    ['다이슨 에어랩', 400000, 500000, 5],
]

item_celine = [
    ['셀린느 스니커즈', 150000, 400000, 2],
    ['셀린느 벨트백', 300000, 600000, 2],
    ['셀린느 후드', 300000, 600000, 2],
    ['셀린느', 100000, 600000, 11],
    ['셀린느 카드지갑', 150000, 450000, 3],
    ['셀린느 크로스백', 550000, 1000000, 3]

]
item_balenciaga = [
    ['발렌시아가', 100000, 700000, 20],
    ['발렌시아가 볼캡', 100000, 250000, 3],
    ['발렌시아가 바람막이', 150000, 550000, 3],
    ['발렌시아가 포플린', 150000, 450000, 3],
    ['발렌시아가 자켓', 200000, 450000, 3],
    ['발렌시아가 후드', 150000, 350000, 4],
    ['발렌시아가 후드집업', 150000, 350000, 3],
    ['발렌시아가 부츠', 150000, 250000, 2],
    ['발렌시아가 뉴러너', 300000, 600000, 3],
    ['발렌시아가 디펜더', 500000, 650000, 2],
    ['발렌시아가 3xl', 450000, 800000, 2],
]
item_prada = [
    ['프라다', 100000, 700000, 20],
    ['프라다 볼캡', 100000, 250000, 2],
    ['프라다 모자', 100000, 250000, 2],
    ['프라다 백팩', 300000, 700000, 2],
    ['프라다 바람막이', 250000, 650000, 2],
    ['프라다 패딩', 400000, 900000, 3],
    ['프라다 자켓', 250000, 650000, 3],
    ['프라다 스니커즈', 150000, 450000, 3],
    ['프라다 로퍼', 200000, 400000, 2],
    ['프라다 크로스백', 450000, 800000, 3],
    ['프라다 트라이앵글', 700000, 1200000, 2],
]
item_sunglasses = [
    ['프라다 선글라스', 150000, 250000, 2],
    ['발렌시아가 선글라스', 150000, 250000, 2],
    ['로에베 선글라스', 150000, 250000, 2],
    ['자크마리마지', 300000, 600000, 3],
]
item_gucci = [
    ['구찌 집업', 200000, 600000, 2],
    ['구찌 트레이닝', 250000, 600000, 2],
    ['구찌 바람막이', 250000, 700000, 2],
    ['구찌 패딩', 500000, 900000, 3],
    ['구찌 후드', 150000, 400000, 3],
	['구찌 저지', 150000, 450000, 3],
    ['구찌 자켓', 150000, 750000, 3],
    ['구찌 팬츠', 150000, 450000, 3],
    ['구찌 스크리너', 150000, 300000, 2],
]
item_moncler = [
    ['몽클레어 패딩', 350000, 700000, 10],
    ['몽클레어', 350000, 700000, 10],
    ['몽클레어 바람막이', 250000, 350000, 3],
    ['몽클레어 3', 350000, 600000, 2],
    ['몽클레어 4', 350000, 600000, 2],
    ['몽클레어 에크린스', 600000, 900000, 2],
    ['몽클레어 산베산', 600000, 900000, 2],
    ['몽클레어 시탈라', 600000, 900000, 2],
    ['몽클레어 카데레', 600000, 900000, 2],
    ['몽클레어 이딜', 600000, 900000, 2],
]

item_louis = [
    ['루이비통 크로스백', 700000, 1400000, 3],
    ['루이비통 오거나이저', 200000, 350000, 3],
    ['고야드 생피에르', 200000, 350000, 2],
    ['루이비통 트레이너', 350000, 800000, 3],
    ['루이비통 가스통', 900000, 1300000, 3],
    ['루이비통 시티키폴', 1200000, 2000000, 2],
]

item_stone = [
    ['스톤아일랜드 패딩', 350000, 600000, 4],
]

item_thombrowne = [
    ['톰브라운 4', 250000, 550000, 3],
    ['톰브라운 3', 350000, 550000, 3],
    ['톰브라운 바람막이', 250000, 650000, 3],
    ['톰브라운 봄버', 250000, 650000, 3],
    ['톰브라운 자켓', 250000, 650000, 3],
]


def worker(items_options):
    # selenium : headless 추가,
    options = webdriver.ChromeOptions()
    options.add_argument("headless")

    # 브라우저 구동
    browser = webdriver.Chrome(options=options)
    browser.implicitly_wait(time_to_wait=10)
    browser.get('https://m.bunjang.co.kr/')

    Category = [] # 0 ~ 1000
    Subject = [] # 0 ~ 1000
    Price = []
    Date = []
    Location = []
    Link = []
    Img_src = []
    Status = []
    for itemname in items_options:
        page = 1

        while True:
            if len(itemname) != 4: # order=price_asc 낮은가격순
                url = "https://m.bunjang.co.kr/search/products?order=price_asc&page={}&q={}".format(page, itemname[0])
            else: # order=date
                url = "https://m.bunjang.co.kr/search/products?order=date&page={}&q={}".format(page, itemname[0])
            browser.get(url)
            print(f"Worker Number:{os.getpid()}, {itemname[0]}")
            # WebDriverWait(browser, 10)
            html = browser.page_source
            html_parser = BeautifulSoup(html, features="html.parser")
            _list = html_parser.find_all(attrs={'alt': '상품 이미지'})

            if page == itemname[3]: # 제품마다 페이지 리밋
                break
            for item in _list:
                aTag = item.parent.parent
                for i, c in enumerate(aTag.children):
                    
                    #번개장터 보면 아이템 하나가 3개의 테이블임
                    # 0:사진, 1:이름,가격,시간,  2:주소
                    if i == 0:
                        Img_src.append(c.find('img')['src'])
                        Status.append('판매중')
                        for img in c.find_all('img'): # img 엘리먼트 찾고, 번개페이/배송비포함/판매완료/예약중 사진 있는데 거기서 판매 완료면 변경
                            if img['alt'] == '판매 완료':
                                Status[-1] = '판매완료'
                    if i == 1:
                        info = c.get_text(separator=';;;')
                        info = info.split(sep=';;;')
                    if i == 2:
                        location = c.get_text()

                try:
                    Category.append(itemname[0])
                    Subject.append(info[0])  # print("제목 : ", info[0])
                    Price.append(info[1])  # print("가격 : ", info[1])
                    if info[2] is None:
                        info[2] = "미 확인"
                    Date.append(info[2])  # print("시간 : ", infor[2])
                    Location.append(location)  # print("위치 : ", Location)
                    Link.append("https://m.bunjang.co.kr{}".format(aTag.attrs['href']))  # print("링크 : ", "https://m.bunjang.co.kr{}".format(aTag.attrs['href']))
                except:
                    Date.append('None')  # print("시간 : ", infor[2])
                    Location.append('None')  # print("위치 : ", Location)
                    Link.append('None')  # print("링크 : ", "https://m.bunjang.co.kr{}".format(aTag.attrs['href']))
                    pass

            page = page + 1
    print("pid: {} done".format(os.getpid()))
    return Category, Subject, Price, Date, Location, Link, Img_src, Status
if __name__ == "__main__":
    items_options = [ *item_clothes,
                     *item_thombrowne, 
                     *item_moncler, 
                     *item_gucci, 
                     *item_prada, 
                     *item_balenciaga, 
                     *item_stone, 
                     *item_bottega, 
                     *item_celine, 
                     *item_louis, 
                     *item_sunglasses,
                    *item_elec,]

    # items_options 리스트를 4개의 동일한 크기의 하위 리스트로 분할합니다.
    num_workers = 8

    n = len(items_options) // num_workers
    items_sublists = [items_options[i * n:(i + 1) * n] for i in range(num_workers)]
    items_sublists[-1] += items_options[num_workers * n:]

    with Pool(num_workers) as p:
        results = p.map(worker, items_sublists)
    for result in results:
        print([len(lst) for lst in result])

    # 각 워커에서 반환된 리스트를 하나로 합칩니다.
    Category = list(chain.from_iterable(result[0] for result in results))
    Subject = list(chain.from_iterable(result[1] for result in results))
    Price = list(chain.from_iterable(result[2] for result in results))
    Date = list(chain.from_iterable(result[3] for result in results))
    Location = list(chain.from_iterable(result[4] for result in results))
    Link = list(chain.from_iterable(result[5] for result in results))
    Img_src = list(chain.from_iterable(result[6] for result in results))
    Status = list(chain.from_iterable(result[7] for result in results))

    Datas = {
        "category" : Category,
        "제목" : Subject,
        "price" : Price,
        "등록일시" : Date,
        "위치" : Location,
        "링크" : Link,
        "src" : Img_src,
        "상태" : Status }

    df = pd.DataFrame(Datas)
    print(len(Category))
    print(len(Subject))
    print(len(Price))
    print(len(Date))
    print(len(Location))
    print(len(Link))
    print(len(Img_src))
    print(len(Status))
    df.drop_duplicates(subset=['src'], inplace=True)
    df = df[df.상태 != '판매완료']
    df = df[df.price != '연락요망'] # 연락요망, 가격협의 전처리
    df.price = df.price.str.replace(';','')  # 금액 str -> int 1,000,000 - > 1000000
    df.price = df.price.str.replace(',','').astype(int)  # 금액 str -> int 1,000,000 - > 1000000

    # 제품, 금액 필터 걸어주기
    def price_filter(df, _info):
        df_filtered = df[(df['category'] == _info[0]) & df['price'].between(_info[1], _info[2])].reset_index(drop=True)
        return df_filtered.sort_values('price')

    # 날짜 변환 코드
    def date_shifter(df):
        def custom_convert(date_str):
            if '주' in date_str:
                return str(int(date_str.split('주')[0]) * 7) + '일 전'
            elif '달' in date_str:
                return str(int(date_str.split('달')[0]) * 30) + '일 전'
            else:
                return date_str

        df['등록일시'] = df['등록일시'].apply(custom_convert)
        return df


    df = date_shifter(df)
    df_concat = pd.concat([price_filter(df, opt) for opt in items_options])


    df_concat.to_excel('./bunjang.xlsx')
