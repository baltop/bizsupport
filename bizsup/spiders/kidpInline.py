import os
import re
import scrapy
from urllib.parse import urlparse, urljoin, unquote
from scrapy_playwright.page import PageMethod


class KidpInlineSpider(scrapy.Spider):
    name = "kidpinline"
    allowed_domains = ['kidp.or.kr']
    start_urls = ['https://kidp.or.kr/?menuno=1202']
    base_url = 'https://kidp.or.kr'
    output_dir = 'output/kidpinline'
    page_count = 0
    max_pages = 2
    items_selector = "table.board01-list tbody tr"


    item_title_selector = "td.left a::text"
    click_selector = "td.left a"

    details_page_main_content_selector = "div#sub_contents"
    attachment_links_selector = "td.end.left.Bleft a"
    
    next_page_url = "https://kidp.or.kr/index.html?menuno=1202&pageIndex={next_page}"
    
    custom_settings = {
        # "PLAYWRIGHT_ABORT_REQUEST": abort_request,  # Aborting unnecessary requests
    }



    def __init__(self, *args, **kwargs):
        super(KidpInlineSpider, self).__init__(*args, **kwargs)
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
                        PageMethod("wait_for_selector", "table.board01-list tbody tr")
                    ]
                }
            )

    async def parse(self, response):
        self.page_count += 1
        self.logger.info(f'Parsing page {self.page_count}')
        
        page = response.meta["playwright_page"]
        
        try:
            # Extract announcement items from the table
            items = response.css(self.items_selector)

            jsstring = response.css("table.board01-list tbody tr td.left a::attr(onclick)").get().strip()
            
            
            for item in items:
                # Skip header row
                if item.css('th'):
                    continue
                
                # Extract details from the list item
                number = item.css('td:nth-child(1)::text').get('').strip()
                title = item.css('td.left a::text').get('').strip()
                date = item.css('td:nth-child(3)::text').get('').strip()
                
                # Get the detail page URL
                detail_url = item.css('td.left a::attr(href)').get()
                
                if detail_url:
                    # Click on the link to open the detail page in a new tab
                    result = await page.evaluate("submitForm(this,'view',18273);")
                    print(result)

                    # await page.click(f'text="{title}"')
                    # Wait for the new page to open
                    new_page = await page.context.wait_for_event('page')
                    # Wait for the page to load
                    await new_page.wait_for_load_state('networkidle')
                    
                    # Extract content from the new page
                    content_html = await new_page.content()
                    # Create a new response object
                    detail_response = response.replace(body=content_html.encode(), url=new_page.url)
                    
                    yield self.parse_detail(detail_response, {
                        'number': number,
                        'title': title,
                        'date': date
                    })
                    
                    # Close the detail page
                    await new_page.close()
            
            # Check if we should proceed to the next page
            if self.page_count < self.max_pages:
                # Find the next page button
                next_page = response.css('div.paging a.next::attr(href)').get()
                if next_page:
                    next_url = urljoin(self.base_url, next_page)
                    yield scrapy.Request(
                        url=next_url,
                        callback=self.parse,
                        meta={
                            "playwright": True,
                            "playwright_include_page": True,
                            "playwright_page_methods": [
                                PageMethod("wait_for_selector", "table.tbl-list")
                            ]
                        }
                    )

        except Exception as e:
            self.logger.error("parse"+ number + " " + title)
            self.logger.error(f"Error occurred: {e}")
        finally:
            await page.close()

    def parse_detail(self, response, meta):
        # Extract metadata from the meta
        number = meta.get('number', '')
        title = meta.get('title', '')
        date = meta.get('date', '')
        
        # Extract a unique ID from the URL
        url_path = urlparse(response.url).path
        detail_id = os.path.basename(url_path).split('.')[0]
        if not detail_id.isdigit():
            detail_id = f"unknown_{hash(response.url) % 10000}"
        
        # Extract content from the detail page
        content_section = response.css('div.bbs-view-cont')
        main_content = content_section.get('') if content_section else ''
        
        # Clean HTML tags if needed
        cleaned_content = re.sub(r'<[^>]+>', ' ', main_content).strip() if main_content else ''
        
        # Create markdown content
        markdown_content = f"""# {title}

## 기본 정보
- 공고 번호: {number}
- 등록일: {date}

## 상세 내용
{cleaned_content}
"""
        
        # Save markdown file
        md_filename = f"{self.output_dir}/{detail_id}.md"
        with open(md_filename, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        self.logger.info(f"Saved markdown file: {md_filename}")
        
        # Process attachments
        attachment_links = response.css('div.bbs-view-file ul li a')
        if attachment_links:
            # Create directory for attachments
            attachment_dir = f"{self.output_dir}/{detail_id}"
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
        
        # Check Content-Disposition header for filename
        content_disposition = response.headers.get('Content-Disposition', b'').decode('utf-8', errors='ignore')
        if 'filename=' in content_disposition:
            server_filename = re.search(r'filename="?([^";]+)', content_disposition).group(1)
            filename = unquote(server_filename)
        
        # If filename is still empty, use a default name based on Content-Type
        if not filename:
            content_type = response.headers.get('Content-Type', b'').decode('utf-8', errors='ignore').split(';')[0]
            extension = self.get_extension_from_content_type(content_type)
            filename = f"attachment_{hash(response.url) % 10000}{extension}"
        
        file_path = os.path.join(attachment_dir, filename)
        
        with open(file_path, 'wb') as f:
            f.write(response.body)
        
        self.logger.info(f"Saved attachment: {file_path}")
    
    def get_extension_from_content_type(self, content_type):
        """Get file extension from content type"""
        content_type_map = {
            'application/pdf': '.pdf',
            'application/msword': '.doc',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document': '.docx',
            'application/vnd.ms-excel': '.xls',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': '.xlsx',
            'application/vnd.ms-powerpoint': '.ppt',
            'application/vnd.openxmlformats-officedocument.presentationml.presentation': '.pptx',
            'image/jpeg': '.jpg',
            'image/png': '.png',
            'text/plain': '.txt',
            'application/zip': '.zip',
            'application/x-hwp': '.hwp'
        }
        
        return content_type_map.get(content_type, '')