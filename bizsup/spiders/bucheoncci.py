import time
from urllib.parse import urljoin
import scrapy
from scrapy.http import Request
from scrapy_playwright.page import PageMethod
import os
import re
from playwright.async_api import Page
from bizsup.spiders.base import BaseSpider
from bizsup.utils import abort_request, create_output_directory, clean_filename, click_and_handle_download
import asyncio
from urllib.parse import urlparse, urlunparse




# 목록 리스트에서 클릭을 하면 응당코드는 200이지만 내용은 잘못된 주소라는 에러 페이지가 리턴됨. 아마도 자바스크립트에 값이 제대로 submit 되지 않는 걸로 보임.


class BuciSpider(BaseSpider):
    name = "buci"
    allowed_domains = ['korcham.net']
    start_urls = ['https://bucheoncci.korcham.net/front/board/boardContentsListPage.do?boardId=10135&menuId=410']
    base_url = 'https://bucheoncci.korcham.net'
    output_dir = 'output/buci'
    page_count = 0
    max_pages = 3
    items_selector = "div.boardlist table tbody tr td.title.c_title a"


    # item_title_selector = "td.title.c_title a::text"
    # click_selector = "td.title.c_title a"
    
    details_page_main_content_selector = "div.contents_detail"
    attachment_links_selector = "ul.file_view li a"
    
    next_page_url = "https://bucheoncci.korcham.net/front/board/boardContentsListPage.do?boardId=10135&menuId=410&miv_pageNo={next_page}"
    
    custom_settings = {
        "PLAYWRIGHT_ABORT_REQUEST": abort_request,  # Aborting unnecessary requests
    }



    def __init__(self, *args, **kwargs):
        super(BuciSpider, self).__init__(*args, **kwargs)
        create_output_directory(self.output_dir)  # Create output directory if it doesn't exist


    # def start_requests(self):
    #     yield scrapy.Request(
    #         url=self.start_urls[0],
    #         meta={
    #             "playwright": True,
    #             "playwright_include_page": True,
    #             "playwright_page_methods": [
    #                 PageMethod("wait_for_selector", "div.boardlist"),  # Wait for the page to load
    #                 # PageMethod("wait_for_timeout", 60000),  # 60 seconds wait
    #             ],
                
    #         })


    # async def parse(self, response):

    #     self.page_count += 1
        
    #     current_url = response.url

    #     try:
    #         page = response.meta["playwright_page"]

    #         items = response.css(self.items_selector)
            
    #         for index, item in enumerate(items, start=1):
    #             # 3초간 휴지
    #             await asyncio.sleep(1)
    #             # Extract details from the list item
    #             number = item.css('td:nth-child(1)::text').get('').strip()
    #             if not number:
    #                 number = str(int(time.time()))
                    
    #             title = item.css(self.item_title_selector).get('').strip()
    #             title_selector = f":nth-match({self.click_selector}, {index})"

    #             # reqeust_url = "https://bucheoncci.korcham.net/front/board/boardContentsView.do?boardId=10135&menuId=410&contId=" + contNumber
    #             yield Request(
    #                 url= current_url,
    #                 meta={
    #                     "playwright": True,
    #                     "playwright_include_page": True,
    #                     "playwright_page_methods": [
    #                         PageMethod("click", title_selector),  # 클릭 이벤트
    #                         PageMethod("wait_for_selector", self.details_page_main_content_selector),
    #                         PageMethod("wait_for_load_state", "domcontentloaded"),  # 페이지 로드 대기
    #                         # PageMethod("wait_for_selector", "div.contents_detail"),
    #                         # PageMethod("wait_for_timeout", 60000),  # 60초 대기
    #                     ],
    #                     "errback": self.errback,
    #                     "number": number,
    #                     "title": title,
    #                 },
    #                 callback=self.parse_details,  # 이동한 페이지를 parse_details로 전달
    #                 dont_filter=True,  # 중복 필터링 비활성화
    #             )
                
    #     except Exception as e:
    #         self.logger.error("parse"+ number + " " + title)
    #         self.logger.error(f"Error occurred: {e}")
    #         self.logger.error(f"Response URL: {response.url}")
    #         # self.logger.error(f"Response body: {response.text}")
    #         self.logger.error(f"Meta data: {response.meta}")
    #     finally:
    #         if page and not page.is_closed():
    #             await page.close()

    #             # Check if we should proceed to the next page
    #     if self.page_count < self.max_pages:
    #         next_page = self.page_count + 1
    #         next_page_url = self.next_page_url.format(next_page=next_page)
    #         self.logger.info(f"Next page URL: {next_page_url}")

    #         yield scrapy.Request(
    #             url=next_page_url, 
    #             callback=self.parse,
    #             meta={
    #             "playwright": True,
    #             "playwright_include_page": True,
    #             "playwright_page_methods": [
    #                 PageMethod("wait_for_selector", "div.boardlist"),  # Wait for the page to load
    #                 # PageMethod("wait_for_timeout", 60000),  # 60 seconds wait
    #             ],
    #         })



    # async def parse_details(self, response):
    #     try:
    #     # Extract data after clicking the link
    #         page = response.meta["playwright_page"]
            
    #         number = response.meta.get('number', '')
    #         title = response.meta.get('title', '')
    #         self.logger.info(f"Number: {number}, Title: {title}")
    #         html = await page.content()
    #         # self.logger.info(f"Page content: {html}")
            
            
            
    #         main_content = response.css(self.details_page_main_content_selector).get('').strip()
    #         cleaned_content = re.sub(r'<[^>]+>', ' ', main_content).strip() if main_content else ''
            
            
    #         markdown_content = f"""# {title}
    #         {cleaned_content}
    #         """
            
    #         # Save markdown file
    #         md_filename = f"{self.output_dir}/{number}.md"
    #         with open(md_filename, 'w', encoding='utf-8') as f:
    #             f.write(markdown_content)
                
                
    #         current_url = response.url
    #         parsed_url = urlparse(current_url)
    #         url_without_params = urlunparse(parsed_url._replace(query=''))
    #         self.logger.info(f"url_without_params: +++++++++++++++++++++++++++++++++++++ {url_without_params}")


    #         attachment_links = response.css(self.attachment_links_selector)
    #         if attachment_links:
    #             # Create directory for attachments
    #             attachment_dir = f"{self.output_dir}/{number}"
    #             # if not os.path.exists(attachment_dir):
    #             #     os.makedirs(attachment_dir)
                
    #             # attachment_links가 단일 Selector인지 확인
    #             # if isinstance(attachment_links, scrapy.selector.Selector):
    #             #     attachment_links = [attachment_links]  # 단일 Selector를 리스트로 변환

    #             # enumerate를 사용하여 index와 link를 순회
    #             for index, link in enumerate(attachment_links, start=1):
    #                 file_url = link.css('::attr(href)').get()

    #                 file_selector = f":nth-match({self.attachment_links_selector}, {index})"

    #                 if file_url:
    #                     filename = link.css('::text').get('').strip()
    #                     filename = clean_filename(filename)
                        
    #                     yield scrapy.Request(
    #                         url=current_url+"&carrot="+str(index),
    #                         # url=file_url,
    #                         callback=self.save_attachment,
    #                         # callback=self.parse_download_info,
    #                         dont_filter=True,  # 중복 필터링 비활성화
    #                         meta={
    #                             'attachment_dir': attachment_dir,
    #                             'filename': filename,
    #                             "playwright": True,
    #                             "playwright_include_page": True,
    #                             # "playwright_download_route": "**/*",
    #                             # "playwright_download_handler": self.handle_download,
    #                             "playwright_page_methods": [
    #                                 # PageMethod("click", selector),  # 동적으로 생성된 selector 전달
    #                                 # PageMethod("click", f"text={clicktext}"),  # 텍스트 기반 선택자 전달
    #                                 # PageMethod("wait_for_load_state", "networkidle")  # 페이지 로드 대기
    #                                 PageMethod(
    #                                     click_and_handle_download, # 정의한 호출 가능한 함수 전달 [1, 7]
    #                                     selector = file_selector, # 함수에 전달할 인자
    #                                     save_path = attachment_dir, # 함수에 전달할 인자
    #                                     file_name = filename
    #                                 ),
    #                                 # PageMethod("wait_for_selector", "div.contents_detail"),
    #                                 # PageMethod("wait_for_load_state", "domcontentloaded"), 
    #                             ],
    #                             "errback": self.errback,
    #                         }
    #                     )
    #     except Exception as e:
    #         self.logger.error("parse_details" + number + " " + title)
    #         self.logger.error(f"Error occurred: {e}")
    #     finally:
    #         # Further processing of html content
    #         if page and not page.is_closed():
    #             await page.close()

    # # def parse_download_info(self, response):
    # #     # click_and_handle_download 함수의 반환 값 (저장된 파일 경로) 가져오기
    # #     # saved_file_path = response.meta["playwright_page_methods"].result
    # #     if filename := response.meta.get("playwright_suggested_filename"):
    # #         attachment_dir = response.meta.get('attachment_dir', '')
    # #     self.logger.info(f"File downloaded and saved ")



    # async def save_attachment(self, response):
    #     page = response.meta["playwright_page"]
    #     filename = response.meta.get("filename")
    #     # current_url = response.url
    #     # if filename2 := response.meta.get("playwright_suggested_filename"):
    #     #     attachment_dir = response.meta.get('attachment_dir', '')
    #     #     file_path = os.path.join(attachment_dir, filename)

    #     #     with open(file_path, 'wb') as f:
    #     #         f.write(response.body)

    #     #     self.logger.info(f"Saved attachment: {file_path}")
    #     yield {
    #         "url": response.url,
    #         "response_cls": response.__class__.__name__,
    #         "first_bytes": response.body[:60],
    #         "filename": filename,
    #     }
    #     if page and not page.is_closed():
    #         await page.close()


    # async def errback(self, failure):
    #     page = failure.request.meta["playwright_page"]
    #     self.logger.error(f"Request failed: {failure.request.url}")
    #     self.logger.error(f"Error: {failure.value}")
    #     self.logger.error(f"Meta data: {failure.request.meta}")
    #     await page.close()
        
        