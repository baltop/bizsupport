import os
import re
import scrapy
from urllib.parse import urlparse, urljoin, unquote
from scrapy_playwright.page import PageMethod

def abort_request(request):
    return (
        request.resource_type in ["image", "media", "stylesheet"]  # Block resource-heavy types
        or any(ext in request.url for ext in [".jpg", ".png", ".gif", ".css", ".mp4", ".webm"])  
        or "google-analytics.com" in request.url
        or "googletagmanager.com" in request.url
        or "atchFileId" in request.url
        or "loginImpl" in request.url
    )
    
    
class GbtpSpider(scrapy.Spider):
    name = 'gbtp'
    allowed_domains = ['gbtp.or.kr']
    start_urls = ['https://www.gbtp.or.kr/user/board.do?bbsId=BBSMSTR_000000000021']
    base_url = 'https://gbtp.or.kr'
    output_dir = 'output/gbtp'
    page_count = 0
    max_pages = 4
    custom_settings = {
        "PLAYWRIGHT_ABORT_REQUEST": abort_request,  # Aborting unnecessary requests
    }

    def __init__(self, *args, **kwargs):
        super(GbtpSpider, self).__init__(*args, **kwargs)
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(
                url=url,
                callback=self.parse,
                meta={
                    "playwright": True,
                    "playwright_include_page": True,
                    "playwright_page_methods": [
                        # PageMethod("wait_for_selector", "table.tablelist")
                    ]
                }
            )

    async def parse(self, response):
        self.page_count += 1
        self.logger.info(f'Parsing page {self.page_count}')
        
        page = response.meta["playwright_page"]
        
        try:
            # Extract announcement items from the table
            items = response.css('table.tablelist tbody tr')
            
            for item in items:
                
                # Extract details from the list item
                number = item.css('td:nth-child(1)::text').get('').strip()
                title = item.css('td.title a::text').get('').strip()
                titleclick = item.css('td.title a::text')

                # Get the detail page URL
                detail_url = item.css('td.title a::attr(href)').get()
                
                if detail_url:
                    # await page.wait_for_selector(f'text="{titleclick}"')  # 클릭할 요소가 로드되었는지 확인
                    # Click on the link to open the detail page in a new tab
                    await page.click(f'text="{title}"')
                    
                    # Wait for the new page to open
                    new_page = await page.context.wait_for_event('page',timeout=180000)

                    # Wait for the page to load
                    await new_page.wait_for_load_state('networkidle')
                    
                    # Extract content from the new page
                    content_html = await new_page.content()
                    # Create a new response object
                    detail_response = response.replace(body=content_html.encode(), url=new_page.url)
                    
                    yield self.parse_detail(detail_response, {
                        'number': number,
                        'title': title
                    })
                    
                    # Close the detail page
                    await new_page.close()
            
            # Check if we should proceed to the next page
            if self.page_count < self.max_pages:
                # Find the next page button
                next_page = self.page_count + 1
                if next_page:
                    next_url = "https://itp.or.kr/intro.asp?tmid=13&PageNum={next_page}"
                    yield scrapy.Request(
                        url=next_url,
                        callback=self.parse,
                        meta={
                            "playwright": True,
                            "playwright_include_page": True,
                            "playwright_page_methods": [
                                PageMethod("wait_for_selector", "table.list")
                            ]
                        }
                    )
                    
        except Exception as e:
            self.logger.error(f"Error occurred: {e}")
            self.logger.error(f"Response URL: {response.url}")
            self.logger.error(f"Response body: {response.text}")
            self.logger.error(f"Meta data: {response.meta}")
        finally:
            await page.close()

    def parse_detail(self, response, meta):
        # Extract metadata from the meta
        number = meta.get('number', '')
        title = meta.get('title', '')
               
        # Extract content from the detail page
        content_section = response.css('div.content')
        main_content = content_section.get('') if content_section else ''
        
        # Clean HTML tags if needed
        cleaned_content = re.sub(r'<[^>]+>', ' ', main_content).strip() if main_content else ''

        
        # Save markdown file
        md_filename = f"{self.output_dir}/{number}.md"
        with open(md_filename, 'w', encoding='utf-8') as f:
            f.write(cleaned_content)
    
        # Process attachments
        attachment_links = response.css('div.dl_view dl dd a')
        if attachment_links:
            # Create directory for attachments
            attachment_dir = f"{self.output_dir}/{number}"
            if not os.path.exists(attachment_dir):
                os.makedirs(attachment_dir)
            
            for link in attachment_links:
                file_url = link.css('::attr(href)').get()
                if file_url:
                    file_url = urljoin(self.base_url, file_url)
                    filename = link.css('::text').get('').strip()
                    
                    yield scrapy.Request(
                        url=file_url,
                        callback=self.save_attachment,
                        meta={
                            'attachment_dir': attachment_dir,
                            'filename': filename
                        }
                    )
        
        return {
            'id': detail_id,
            'title': title,
            'date': date,
            'content': cleaned_content
        }
    
    def save_attachment(self, response):
        attachment_dir = response.meta.get('attachment_dir', '')
        filename = response.meta.get('filename', '')
        
        file_path = os.path.join(attachment_dir, filename)
        
        with open(file_path, 'wb') as f:
            f.write(response.body)
        
        self.logger.info(f"Saved attachment: {file_path}")
    
