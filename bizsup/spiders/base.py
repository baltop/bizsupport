import scrapy
from scrapy.http import Request
from scrapy_playwright.page import PageMethod
import os
import re
import asyncio
import time
import json
import hashlib
from datetime import datetime
from urllib.parse import urlparse, urlunparse
from bizsup.utils import clean_filename, click_and_handle_download, create_output_directory

class BaseSpider(scrapy.Spider):
    name = "base_spider"
    allowed_domains = ['gbsa.or.kr']
    start_urls = ['https://www.gbsa.or.kr/board/notice.do']
    base_url = 'https://gbsa.or.kr'
    output_dir = 'output/gbsa'

    page_count = 0
    max_pages = 2
    
    items_selector = "table.bbs-list tbody tr"

    details_page_main_content_selector = "div#content"

    attachment_links_selector = "table.bbs-view tbody tr td ul li a"

    next_page_url = "https://www.gbsa.or.kr/board/notice.do?pageIndex={next_page}&searchCnd=0&searchWrd=&ozcsrf="
    
    custom_settings = {
        "PLAYWRIGHT_ABORT_REQUEST": None,  # override in subclass if needed
    }

    def __init__(self, *args, **kwargs):
        super(BaseSpider, self).__init__(*args, **kwargs)
        create_output_directory(self.output_dir)
        
        # 중복 체크 관련
        self.processed_titles_file = f"{self.output_dir}/processed_titles.json"
        self.processed_titles = set()
        self.enable_duplicate_check = True
        self.duplicate_threshold = 3  # 동일 제목 3개 발견시 조기 종료
        self.consecutive_duplicates = 0  # 연속 중복 카운터
        
        # 처리된 제목 목록 로드
        self.load_processed_titles()
    
    def normalize_title(self, title: str) -> str:
        """제목 정규화 - 중복 체크용"""
        if not title:
            return ""
        
        # 앞뒤 공백 제거
        normalized = title.strip()
        
        # 연속된 공백을 하나로
        normalized = re.sub(r'\s+', ' ', normalized)
        
        # 특수문자 제거 (일부 허용)
        normalized = re.sub(r'[^\w\s가-힣()-]', '', normalized)
        
        # 소문자 변환 (영문의 경우)
        normalized = normalized.lower()
        
        return normalized
    
    def get_title_hash(self, title: str) -> str:
        """제목의 해시값 생성"""
        normalized = self.normalize_title(title)
        return hashlib.md5(normalized.encode('utf-8')).hexdigest()
    
    def load_processed_titles(self):
        """처리된 제목 목록 로드"""
        if not self.enable_duplicate_check:
            return
        
        try:
            if os.path.exists(self.processed_titles_file):
                with open(self.processed_titles_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # 제목 해시만 로드
                    self.processed_titles = set(data.get('title_hashes', []))
                    self.logger.info(f"기존 처리된 공고 {len(self.processed_titles)}개 로드")
            else:
                self.processed_titles = set()
                self.logger.info("새로운 처리된 제목 파일 생성")
        except Exception as e:
            self.logger.error(f"처리된 제목 로드 실패: {e}")
            self.processed_titles = set()
    
    def save_processed_titles(self):
        """처리된 제목 목록 저장"""
        if not self.enable_duplicate_check or not self.processed_titles_file:
            return
        
        try:
            os.makedirs(os.path.dirname(self.processed_titles_file), exist_ok=True)
            
            data = {
                'title_hashes': list(self.processed_titles),
                'last_updated': datetime.now().isoformat(),
                'total_count': len(self.processed_titles)
            }
            
            with open(self.processed_titles_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                
            self.logger.info(f"처리된 제목 {len(self.processed_titles)}개 저장 완료")
        except Exception as e:
            self.logger.error(f"처리된 제목 저장 실패: {e}")
    
    def is_title_processed(self, title: str) -> bool:
        """제목이 이미 처리되었는지 확인"""
        if not self.enable_duplicate_check:
            return False
        
        title_hash = self.get_title_hash(title)
        return title_hash in self.processed_titles
    
    def add_processed_title(self, title: str):
        """처리된 제목 추가"""
        if not self.enable_duplicate_check:
            return
        
        title_hash = self.get_title_hash(title)
        self.processed_titles.add(title_hash)


    async def start(self):
        yield scrapy.Request(
            url=self.start_urls[0],
            meta={
                "playwright": True,
                "playwright_include_page": True,
                "playwright_page_methods": [
                    PageMethod("wait_for_selector", self.items_selector),
                ],
            })


    async def parse(self, response):
        self.page_count += 1
        current_url = response.url
        try:
            page = response.meta["playwright_page"]
            items = response.css(self.items_selector)

            for index, item in enumerate(items, start=1):
                await asyncio.sleep(3)
                # number = ''

                # 대부분 items는 table tag 아래 있음. 가끔 div ul 로 된 사이트도 있음.
                # if ' tr ' in self.items_selector:
                #     # items_selector를 tr 까지만 남기고 나머지는 지워버림
                #     base_str = self.items_selector.split('tr')[0]
                #     num_selector = f"{base_str} tr:nth-of-type({index}) td:nth-child(1) *::text"
                #     number = response.css(num_selector).get('').strip()
                # if not number:
                #     number = str(int(time.time()))

                # 각 아이템에서 개별적으로 제목 추출
                # 먼저 일반적인 링크 텍스트 시도
                # op_sel = response.css(f":nth-match({self.items_selector}, {index} )")
                title = item.css(" *::text").get('').strip()

                if not title:
                    # 마지막으로 모든 텍스트에서 첫 번째 추출
                    title = response.css(f"{self.items_selector} *::text").getall().strip()
                    
                self.logger.info(f"Title: {title}")
                
                yield Request(
                    url=current_url,
                    meta={
                        "playwright": True,
                        "playwright_include_page": True,
                        "playwright_page_methods": [
                            PageMethod("click", f":nth-match({self.items_selector}, {index})"),
                            PageMethod("wait_for_selector", self.details_page_main_content_selector),
                            PageMethod("wait_for_load_state", "domcontentloaded"),
                        ],
                        "errback": self.errback,
                        "title": title,
                    },
                    callback=self.parse_details,
                    dont_filter=True,
                )
        except Exception as e:

            self.logger.error(f"Error occurred: {e}")
            
            self.logger.error(f"Response URL: {response.url}")
            self.logger.error(f"Meta data: {response.meta}")
            self.logger.error("parse " + title)
        finally:
            if page and not page.is_closed():
                await page.close()
        if self.page_count < self.max_pages:
            next_page = self.page_count + 1
            next_page_url = self.next_page_url.format(next_page=next_page)
            self.logger.info(f"Next page URL: {next_page_url}")
            yield scrapy.Request(
                url=next_page_url,
                callback=self.parse,
                meta={
                    "playwright": True,
                    "playwright_include_page": True,
                    "playwright_page_methods": [
                        PageMethod("wait_for_selector", self.items_selector),
                    ],
                })

    async def parse_details(self, response):
        try:
            page = response.meta["playwright_page"]
            
            title = response.meta.get('title', '')
            
            # 처리된 제목으로 추가
            self.add_processed_title(title)
            main_content = response.css(self.details_page_main_content_selector).get('').strip()
            cleaned_content = re.sub(r'<[^>]+>', ' ', main_content).strip() if main_content else ''
            # Create folder based on announcement title
            title_folder_name = clean_filename(title) 
            title_folder_path = f"{self.output_dir}/{title_folder_name}"
            
            # Create title folder if it doesn't exist
            if not os.path.exists(title_folder_path):
                os.makedirs(title_folder_path)
            
            markdown_content = f"""# {title}

## 공고 내용
{cleaned_content}

---
URL: {response.url}
작성일: {time.strftime('%Y-%m-%d %H:%M:%S')}
"""
            md_filename = f"{title_folder_path}/content.md"
            with open(md_filename, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            current_url = response.url
            parsed_url = urlparse(current_url)
            url_without_params = urlunparse(parsed_url._replace(query=''))
            self.logger.info(f"url_without_params: +++++++++++++++++++++++++++++++++++++ {url_without_params}")
            attachment_links = response.css(self.attachment_links_selector)
            if attachment_links:
                attachment_dir = f"{title_folder_path}/attachments"
                if not os.path.exists(attachment_dir):
                    os.makedirs(attachment_dir)
                if isinstance(attachment_links, scrapy.selector.Selector):
                    attachment_links = [attachment_links]
                for index, link in enumerate(attachment_links, start=1):
                    file_url = link.css('::attr(href)').get()
                    file_selector = f":nth-match({self.attachment_links_selector}, {index})"
                    if file_url:
                        filename = link.css(' *::text').get('').strip()
                        filename = clean_filename(filename)
                        yield scrapy.Request(
                            url=current_url,
                            callback=self.save_attachment,
                            dont_filter=True,
                            meta={
                                'attachment_dir': attachment_dir,
                                'filename': filename,
                                "playwright": True,
                                "playwright_include_page": True,
                                "playwright_page_methods": [
                                    PageMethod(
                                        click_and_handle_download,
                                        selector = file_selector,
                                        save_path = attachment_dir,
                                        file_name = filename
                                    ),
                                ],
                                "errback": self.errback,
                            }
                        )
        except Exception as e:
            self.logger.error("parse_details " + title)
            self.logger.error(f"Error occurred: {e}")
        finally:
            if page and not page.is_closed():
                await page.close()

    async def save_attachment(self, response):
        page = response.meta["playwright_page"]
        filename = response.meta.get("filename")
        yield {
            "url": response.url,
            "response_cls": response.__class__.__name__,
            "first_bytes": response.body[:60],
            "filename": response.meta.get("playwright_suggested_filename"),
        }
        if page and not page.is_closed():
            await page.close()

    async def errback(self, failure):
        page = failure.request.meta["playwright_page"]
        self.logger.error(f"Request failed: {failure.request.url}")
        self.logger.error(f"Error: {failure.value}")
        self.logger.error(f"Meta data: {failure.request.meta}")
        await page.close()