from fastapi.responses import HTMLResponse
from app.services.search_service import SearchService

html_template = """
<html>
<head>
    <style>
        .price {{
            font-size: 30px;
            font-weight: bold;
        }}
        .title {{
            font-size: 24px;
            font-weight: bold;
        }}
        .location-date {{
            font-size: 18px;
            margin-top: 10px;
        }}
        .item-container {{
            display: flex;
            flex-wrap: wrap;
        }}
        .item {{
            width: 16%;
            padding: 10px;
            box-sizing: border-box;
        }}
    </style>
</head>
    <body>
        <h1>쇼핑몰 상품</h1>
        <form action="/items/" method="get">
            <input type="text" name="search_query" placeholder="검색어를 입력하세요">
            <input type="submit" value="검색">
        </form>
        <div class="item-container">
        {items}
        </div>
        <div class="pagination">
            <a href="/items/?page={prev_page}&search_query={search_query}">이전 페이지</a>
            <a href="/items/?page={next_page}&search_query={search_query}">다음 페이지</a>
        </div>
    </body>
</html>
"""

search_service = SearchService()

async def render_items(page: int, page_size: int, search_query: str = None):
    items = await search_service.search_items(page, page_size, search_query)

    items_html = ''
    for item in items:
        item_html = f'''
        <div class="item">
            <a href="{item['링크']}" target="_blank">
                <img src="{item['src']}" alt="Product Image" loading="lazy">
            </a><br>
            <span class="price">{item['price']}원</span><br>
            <span class="title">{item['제목']}</span><br>
            <span class="location-date">
                위치: {item['위치']}<br>
                등록일시: {item['등록일시']}
            </span>
        </div>
        '''
        items_html += item_html

    html = html_template.format(
        items=items_html,
        prev_page=max(1, page-1),
        next_page=page+1,
        search_query=search_query or ''
    )

    return HTMLResponse(content=html, status_code=200)
