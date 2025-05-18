import time
from urllib.parse import urljoin
import scrapy
from scrapy.http import Request
from scrapy_playwright.page import PageMethod
import os
import re
from playwright.async_api import Page
from bizsup.utils import abort_request, create_output_directory, make_selector, clean_filename
import asyncio
from urllib.parse import urlparse, urlunparse

class GicaSpider(scrapy.Spider):
    name = "gica"
    allowed_domains = ['gica.or.kr']
    start_urls = ['https://www.gica.or.kr/Home/H40000/H40100/boardList?page=1']
    base_url = 'https://gica.or.kr'
    output_dir = 'output/gica'
    page_count = 0
    max_pages = 2
    items_selector = "table.table_bbs tbody tr"
    item_num_selector = "td:nth-child(1)::text"

    item_title_selector = "td.subject a::text"
    click_selector = "td.subject a"
    
    details_page_main_content_selector = "div.contents_wrap"
    attachment_links_selector = "div.file_wrap a"
    
    next_page_url = "https://www.gica.or.kr/Home/H40000/H40100/boardList?page={next_page}"
    
    custom_settings = {
        "PLAYWRIGHT_ABORT_REQUEST": abort_request,  # Aborting unnecessary requests
    }



    def __init__(self, *args, **kwargs):
        super(GicaSpider, self).__init__(*args, **kwargs)
        create_output_directory(self.output_dir)  # Create output directory if it doesn't exist


    def start_requests(self):
        yield scrapy.Request(
            url=self.start_urls[0],
            meta={
                "playwright": True,
                "playwright_include_page": True
            })


    async def parse(self, response):
        self.page_count += 1
        
        current_url = response.url

        try:
            page = response.meta["playwright_page"]

            items = response.css(self.items_selector)
            
            for index, item in enumerate(items, start=1):
                # 3초간 휴지
                await asyncio.sleep(3)
                # Extract details from the list item
                number = item.css('td:nth-child(1)::text').get('').strip()
                if not number:
                    number = str(int(time.time()))
                    
                title = item.css(self.item_title_selector).get('').strip()
                title_selector = f":nth-match({self.click_selector}, {index})"

                yield Request(
                    url= current_url + f"&carrot={number}",
                    meta={
                        "playwright": True,
                        "playwright_include_page": True,
                        "playwright_page_methods": [
                            PageMethod("click", title_selector),  # 클릭 이벤트
                            PageMethod("wait_for_load_state", "domcontentloaded"),  # 페이지 로드 대기
                            # PageMethod("wait_for_timeout", 60000),  # 60초 대기
                        ],
                        "errback": self.errback,
                        "number": number,
                        "title": title,
                    },
                    callback=self.parse_details,  # 이동한 페이지를 parse_details로 전달
                    # dont_filter=True,  # 중복 필터링 비활성화
                )
                
        except Exception as e:
            self.looger.error("parse"+ number + " " + title)
            self.logger.error(f"Error occurred: {e}")
            self.logger.error(f"Response URL: {response.url}")
            # self.logger.error(f"Response body: {response.text}")
            self.logger.error(f"Meta data: {response.meta}")
        finally:
            if page and not page.is_closed():
                await page.close()

                # Check if we should proceed to the next page
        if self.page_count < self.max_pages:
            next_page = self.page_count + 1
            next_page_url = self.next_page_url.format(next_page=next_page)
            self.logger.info(f"Next page URL: {next_page_url}")

            yield scrapy.Request(
                url=next_page_url, 
                callback=self.parse,
                meta={
                "playwright": True,
                "playwright_include_page": True
            })



    async def parse_details(self, response):
        try:
        # Extract data after clicking the link
            page = response.meta["playwright_page"]
            
            number = response.meta.get('number', '')
            title = response.meta.get('title', '')
            self.logger.info(f"Number: {number}, Title: {title}")
            # html = await page.content()
            # self.logger.info(f"Page content: {html}")
            
            
            
            main_content = response.css(self.details_page_main_content_selector).get('').strip()
            cleaned_content = re.sub(r'<[^>]+>', ' ', main_content).strip() if main_content else ''
            
            
            markdown_content = f"""# {title}
            {cleaned_content}
            """
            
            # Save markdown file
            md_filename = f"{self.output_dir}/{number}.md"
            with open(md_filename, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
                
                
            current_url = response.url
            parsed_url = urlparse(current_url)
            url_without_params = urlunparse(parsed_url._replace(query=''))
            self.logger.info(f"url_without_params: +++++++++++++++++++++++++++++++++++++ {url_without_params}")


            attachment_links = response.css(self.attachment_links_selector)
            if attachment_links:
                # Create directory for attachments
                attachment_dir = f"{self.output_dir}/{number}"
                if not os.path.exists(attachment_dir):
                    os.makedirs(attachment_dir)
                
                # attachment_links가 단일 Selector인지 확인
                if isinstance(attachment_links, scrapy.selector.Selector):
                    attachment_links = [attachment_links]  # 단일 Selector를 리스트로 변환

                # enumerate를 사용하여 index와 link를 순회
                for index, link in enumerate(attachment_links, start=1):
                    file_url = link.css('::attr(href)').get()

                    file_selector = f":nth-match({self.attachment_links_selector}, {index})"

                    if file_url:
                        filename = link.css('::text').get('').strip()
                        filename = clean_filename(filename)
                        
                        yield scrapy.Request(
                            url=current_url+"&carrot="+str(index),
                            # url=file_url,
                            callback=self.save_attachment,
                            # callback=self.parse_download_info,
                            dont_filter=True,  # 중복 필터링 비활성화
                            meta={
                                'attachment_dir': attachment_dir,
                                'filename': filename,
                                "playwright": True,
                                "playwright_include_page": True,
                                # "playwright_download_route": "**/*",
                                # "playwright_download_handler": self.handle_download,
                                "playwright_page_methods": [
                                    # PageMethod("click", selector),  # 동적으로 생성된 selector 전달
                                    # PageMethod("click", f"text={clicktext}"),  # 텍스트 기반 선택자 전달
                                    # PageMethod("wait_for_load_state", "networkidle")  # 페이지 로드 대기
                                    PageMethod(
                                        click_and_handle_download, # 정의한 호출 가능한 함수 전달 [1, 7]
                                        selector = file_selector, # 함수에 전달할 인자
                                        save_path = attachment_dir, # 함수에 전달할 인자
                                        file_name = filename
                                    ),
                                    # PageMethod("wait_for_load_state", "domcontentloaded"), 
                                ],
                                "errback": self.errback,
                            }
                        )
        except Exception as e:
            self.logger.error("parse_details" + number + " " + title)
            self.logger.error(f"Error occurred: {e}")
        finally:
            # Further processing of html content
            if page and not page.is_closed():
                await page.close()

    # def parse_download_info(self, response):
    #     # click_and_handle_download 함수의 반환 값 (저장된 파일 경로) 가져오기
    #     # saved_file_path = response.meta["playwright_page_methods"].result
    #     if filename := response.meta.get("playwright_suggested_filename"):
    #         attachment_dir = response.meta.get('attachment_dir', '')
    #     self.logger.info(f"File downloaded and saved ")



    async def save_attachment(self, response):
        page = response.meta["playwright_page"]
        filename = response.meta.get("filename")
        # current_url = response.url
        # if filename2 := response.meta.get("playwright_suggested_filename"):
        #     attachment_dir = response.meta.get('attachment_dir', '')
        #     file_path = os.path.join(attachment_dir, filename)

        #     with open(file_path, 'wb') as f:
        #         f.write(response.body)

        #     self.logger.info(f"Saved attachment: {file_path}")
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
        await page.close()
        
        

async def click_and_handle_download(page: Page, selector: str, save_path: str, file_name: str) -> str:
    try:
        # 다운로드를 기다리는 context manager 시작 [4]
        async with page.expect_download() as download_info:
            # 다운로드를 트리거하는 요소 클릭 (Locators 사용 권장) [4]
            # Playwright는 액션 수행 전에 요소가 보이고, 안정적인지 등을 자동으로 기다립니다 [8, 9]
            locator = page.locator(selector) # CSS 또는 XPath 셀렉터 가능 [10]
            await locator.click() # Playwright Locator click 메서드 사용 [5, 11]

        # 다운로드 객체 가져오기 [4]
        download = await download_info.value

        if re.search(r'\.[a-zA-Z]{2,4}$', download.suggested_filename): 
            cur_file_name = download.suggested_filename
        else:
            cur_file_name = file_name


        # 파일 저장 경로 설정 (원하는 경로와 다운로드된 파일의 추천 이름 조합) [4]
        full_save_path = f"{save_path}/{cur_file_name}"

        # 파일 저장 [4]
        await download.save_as(full_save_path)

    except Exception as e:
        print("click_and_handle_download " + save_path + " " + file_name)
        print(f"Error occurred: {e}")
        exit()
    # 저장된 파일 경로를 결과로 반환 [1]
    return full_save_path
