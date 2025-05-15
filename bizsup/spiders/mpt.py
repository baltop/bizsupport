import time
from urllib.parse import urljoin
import scrapy
from scrapy.http import Request
from scrapy_playwright.page import PageMethod
import os
import re
from playwright.async_api import Page


def abort_request(request):
    return (
        request.resource_type in ["image", "media", "stylesheet"]  # Block resource-heavy types
        or any(ext in request.url for ext in [".jpg", ".png", ".gif", ".css", ".mp4", ".webm"])  
        or "google-analytics.com" in request.url
        or "googletagmanager.com" in request.url
    )



class MptSpider(scrapy.Spider):
    name = "mpt"
    allowed_domains = ['itp.or.kr']
    start_urls = ['https://itp.or.kr/intro.asp?tmid=13']
    base_url = 'https://www.itp.or.kr'
    output_dir = 'output/mtp'
    page_count = 0
    max_pages = 1
    items_selector = "table.list.fixed tbody tr"
    click_selector = "table.list.fixed tbody tr  td.subject a"
    details_page_main_content_selector = "div#content"
    attachment_links_selector = "div.dl_view dl dd a"
    custom_settings = {
        "PLAYWRIGHT_ABORT_REQUEST": abort_request,  # Aborting unnecessary requests
    }

    def __init__(self, *args, **kwargs):
        super(MptSpider, self).__init__(*args, **kwargs)
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)




    async def parse(self, response):
        self.page_count += 1
        
        try :
            items = response.css(self.items_selector)
            
            for index, item in enumerate(items, start=1):
                # Extract details from the list item
                number = item.css('td:nth-child(1)::text').get('').strip()
                if not number:
                    number = str(int(time.time()))
                    
                title = item.css('td.subject a::text').get('').strip()

                if number != '2871':
                    self.logger.info(f"Number not found for item {index}, skipping...")
                    continue

                # 동적으로 selector 생성
                # items_selector에서 tr 이나 ul 을 찾아서 nth-child(index)를 추가하여 생성
                selector = self.make_selector(self.click_selector, index)
                # selector = f"table.bdListTbl tbody tr:nth-child({index}) td.subject a"
            
                yield Request(
                    url=f"https://itp.or.kr/intro.asp?tmid=13&seq={number}",
                    meta={
                        "playwright": True,
                        "playwright_include_page": True,
                        "playwright_page_methods": [
                            PageMethod("click", selector),  # 클릭 이벤트
                            PageMethod("wait_for_load_state", "networkidle")  # 페이지 로드 대기
                        ],
                        "errback": self.errback,
                        "number": number,
                        "title": title,
                    },
                    callback=self.parse_details,  # 이동한 페이지를 parse_details로 전달
                    dont_filter=True,  # 중복 필터링 비활성화
                )
                
        except Exception as e:
            self.logger.error(f"Error occurred: {e}")
            self.logger.error(f"Response URL: {response.url}")
            # self.logger.error(f"Response body: {response.text}")
            self.logger.error(f"Meta data: {response.meta}")
        # finally:
        #     await page.close()

                # Check if we should proceed to the next page
        if self.page_count < self.max_pages:
            next_page = self.page_count + 1
            next_page_url = f"https://www.btp.or.kr/kor/CMS/Board/Board.do?robot=Y&mCode=MN013&page={next_page}"

            yield scrapy.Request(url=next_page_url, callback=self.parse)



    async def parse_details(self, response):
         # Extract data after clicking the link
        # page = response.meta["playwright_page"]
        
        number = response.meta.get('number', '')
        title = response.meta.get('title', '')
        self.logger.info(f"Number: {number}, Title: {title}")
        # html = await page.content()
        # self.logger.info(f"Page content: {html}")
        self.logger.info(f"Page content: +++++++++++++++++++++++++++++++++++++")
        
        
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
                if index > 1:
                    continue

                file_url = link.css('::attr(href)').get()
                # index = index + 1  # nth-child는 1부터 시작하므로 1을 더함
                if file_url:
                    file_url = urljoin(self.base_url, file_url)
                    filename = link.css('span::text').get('').strip()
                    # filename 중간에 \n이 있으면 삭제
                    filename = filename.replace('\n', '').replace('(', '').replace(')', '').replace('\r', '').strip()
                    self.logger.info(f"Filename: {filename}")
                    match = re.search(r'\.[a-zA-Z]{3,4}', filename)
                    if match:
                        # 확장자 위치까지만 포함하여 자름
                        filename = filename[:match.end()]
                    # filename = self.clean_filename(filename)
                    
                    selector = self.make_selector(self.attachment_links_selector, index)
                    selector = selector + " span::text"  # span 태그의 텍스트를 선택하는 selector
                    clicktext = response.css(selector).get().strip()
                    self.logger.info(f"Click text: {clicktext}")
                    selector = f"table.bdListTbl tbody tr:  td.subject a"                    
                    # selector = "//div[@class='board-biz-file']//ul[@class='file-list']//li[1]//a//span"
                    
                    yield scrapy.Request(
                        # url=current_url,
                        url=file_url,
                        # callback=self.save_attachment,
                        callback=self.parse_download_info,
                        # dont_filter=True,  # 중복 필터링 비활성화
                        meta={
                            'attachment_dir': attachment_dir,
                            'filename': filename,
                            "playwright": True,
                            "playwright_include_page": True,
                            "playwright_page_methods": [
                                PageMethod("click", selector),  # 동적으로 생성된 selector 전달
                                # PageMethod("click", text_selector),  # 텍스트 기반 선택자 전달
                                PageMethod("wait_for_load_state", "networkidle")  # 페이지 로드 대기
                                # PageMethod(
                                #     click_and_handle_download, # 정의한 호출 가능한 함수 전달 [1, 7]
                                #     selector = selector, # 함수에 전달할 인자
                                #     save_path = attachment_dir # 함수에 전달할 인자
                                # ),
                            ],
                            "errback": self.errback,
                        }
                    )            
                    
        # Further processing of html content
        # await page.close()

    def parse_download_info(self, response):
        # click_and_handle_download 함수의 반환 값 (저장된 파일 경로) 가져오기
        # saved_file_path = response.meta["playwright_page_methods"].result
        self.logger.info(f"File downloaded and saved ")



    def save_attachment(self, response):
        attachment_dir = response.meta.get('attachment_dir', '')
        filename = response.meta.get('filename', '')
        
        file_path = os.path.join(attachment_dir, filename)
        
        with open(file_path, 'wb') as f:
            f.write(response.body)
        
        self.logger.info(f"Saved attachment: {file_path}")

    def clean_filename(filename):
        # 정규식을 사용하여 .알파벳3글자 형식의 확장자를 찾음
        match = re.search(r'\.[a-zA-Z]{3,4}', filename)
        if match:
            # 확장자 위치까지만 포함하여 자름
            return filename[:match.end()]
        return filename  # 확장자가 없으면 원래 문자열 반환
    
    
    def make_selector(self, items_selector, index):
        # items_selector에서 tr 이나 ul 을 찾아서 nth-child(index)를 추가하여 생성
        if 'tr' in items_selector:
            selector = re.sub(r'( tr(\.[a-zA-Z0-9_-]+)?)', rf'\1:nth-child({index})', items_selector)
        elif 'li' in items_selector:
            selector = re.sub(r'( li(\.[a-zA-Z0-9_-]+)?)', rf'\1:nth-child({index})', items_selector)
        else:
            raise ValueError("Invalid items_selector format")
        
        return selector


    async def errback(self, failure):
        page = failure.request.meta["playwright_page"]
        await page.close()
        
        
async def click_and_handle_download(page: Page, selector: str, save_path: str) -> str:
    # 다운로드를 기다리는 context manager 시작 [4]
    async with page.expect_download() as download_info:
        # 다운로드를 트리거하는 요소 클릭 (Locators 사용 권장) [4]
        # Playwright는 액션 수행 전에 요소가 보이고, 안정적인지 등을 자동으로 기다립니다 [8, 9]
        locator = page.locator(selector) # CSS 또는 XPath 셀렉터 가능 [10]
        await locator.click() # Playwright Locator click 메서드 사용 [5, 11]

    # 다운로드 객체 가져오기 [4]
    download = await download_info.value

    # 파일 저장 경로 설정 (원하는 경로와 다운로드된 파일의 추천 이름 조합) [4]
    full_save_path = f"{save_path}/{download.suggested_filename}"

    # 파일 저장 [4]
    await download.save_as(full_save_path)

    # 저장된 파일 경로를 결과로 반환 [1]
    return full_save_path
