from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from concurrent.futures import ThreadPoolExecutor
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import asyncio

# 유저 정보 설정
user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15"

# 웹드라이버 설정
service = ChromeService(executable_path=ChromeDriverManager().install())
options = ChromeOptions()
options.add_argument("--headless")
options.add_argument(f"user-agent={user_agent}")

executor = ThreadPoolExecutor()

ss = {}

def get_mt_cr(url):
    # 크롬 웹드라이버 실행
    browser = webdriver.Chrome(service=service, options=options)
    browser.get(url)

    # 페이지가 완전히 로드될 때까지 대기
    WebDriverWait(browser, 5).until(EC.presence_of_element_located((By.TAG_NAME, "html")))

    # 업데이트된 페이지 소스를 변수에 저장
    html_source_updated = browser.page_source
    soup = BeautifulSoup(html_source_updated, 'html.parser')

    # head 요소 내에서 메타태그 찾기
    head = soup.find('html')
    meta_tags = {}
    imsi = []

    if head:
        # 타이틀 메타태그 찾기
        title_meta = head.find('meta', attrs={'property': 'og:title'})
        if title_meta:
            meta_tags['title'] = title_meta['content']
        else:
            meta_tags['title'] = "타이틀 메타태그를 찾을 수 없습니다."

        # 이미지 메타태그 찾기
        image_meta = head.find('meta', attrs={'property': 'og:image'})
        if image_meta:
            meta_tags['image_url'] = image_meta['content']
        else:
            meta_tags['image_url'] = "이미지 메타태그를 찾을 수 없습니다."

        # 설명 메타태그 찾기
        description_meta = head.find('meta', attrs={'property': 'og:description'})
        if description_meta:
            meta_tags['description'] = description_meta['content']
        else:
            meta_tags['description'] = "설명 메타태그를 찾을 수 없습니다."
        
        imsi = (title_meta, image_meta, description_meta)
    else:
        meta_tags['error'] = "head 요소를 찾을 수 없습니다."
    
    return meta_tags

# FastAPI 인스턴스 생성
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 모든 출처를 허용하려면 "*"를 사용합니다. 필요에 따라 특정 출처를 추가할 수 있습니다.
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# GET 메서드로 접근할 엔드포인트 정의
@app.get("/get")
async def get_url(url: str):
    # 받아온 URL을 변수에 저장
    stored_url = url
    result = await asyncio.to_thread(get_mt_cr, stored_url)
    return result
