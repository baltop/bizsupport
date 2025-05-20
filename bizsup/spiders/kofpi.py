import time
from urllib.parse import urljoin
import scrapy
from scrapy.http import Request
from scrapy_playwright.page import PageMethod
import os
import re
from playwright.async_api import Page
from bizsup.utils import abort_request, create_output_directory, make_selector, clean_filename, click_and_handle_download
import asyncio
from urllib.parse import urlparse, urlunparse

class KofpiSpider(scrapy.Spider):
    name = "kofpi"
    allowed_domains = ['kofpi.or.kr']
    start_urls = ['https://www.kofpi.or.kr/notice/notice_01.do']
    base_url = 'https://www.kofpi.or.kr'
    output_dir = 'output/kofpi'
    page_count = 0
    max_pages = 2
    items_selector = "table.table_list tbody tr"
    item_num_selector = "td:nth-child(1)::text"

    item_title_selector = "td.title a::text"
    click_selector = "td.title a"
    
    details_page_main_content_selector = "table.table_view"
    attachment_links_selector = "ul.infile_list li a"
    
    next_page_url = "https://www.kofpi.or.kr/notice/notice_01.do?cPage={next_page}"
    
    custom_settings = {
        # "PLAYWRIGHT_ABORT_REQUEST": abort_request,  # Aborting unnecessary requests
    }

    def __init__(self, *args, **kwargs):
        super(KofpiSpider, self).__init__(*args, **kwargs)
        create_output_directory(self.output_dir)  # Create output directory if it doesn't exist

    async def start(self):
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

                # Extract details from the list item
                number = item.css(self.item_num_selector).get('').strip()
                if not number:
                    number = str(int(time.time()))
                    
                title = item.css(self.item_title_selector).get('').strip()
                title_selector = f":nth-match({self.click_selector}, {index})"

                # Use page.click() directly instead of PageMethod
                locator = page.locator("text=2025년도 산림과학기술 출연연구개발사업 제3차 신규과제 선정계획 공고")
                await page.goto("https://www.kofpi.or.kr/notice/notice_01.do")
                await page.wait_for_load_state("load")
                await asyncio.sleep(180)
                await page.click("text=2025년도 산림과학기술 출연연구개발사업 제3차 신규과제 선정계획 공고")
                # page.wait_for_navigation()
                # await locator.click()
                await page.wait_for_load_state("load")
                
                # Get the current URL after clicking
                # current_detail_url = await page.url()
                html = await page.content()
                current_detail_url = page.url
                self.logger.info(f"Current detail URL: {current_detail_url}")
                
                # Continue with processing the detail page
                yield Request(
                    url=current_detail_url,
                    meta={
                        "playwright": True,
                        "playwright_include_page": True,
                        "errback": self.errback,
                        "number": number,
                        "title": title,
                    },
                    callback=self.parse_details,
                )
                
                # Navigate back to the list page to continue processing
                await page.go_back()
                await page.wait_for_load_state("domcontentloaded")
                
        except Exception as e:
            self.logger.error(f"Error in parse: {e}")
            self.logger.error(f"Response URL: {response.url}")
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
            page = response.meta["playwright_page"]
            
            number = response.meta.get('number', '')
            title = response.meta.get('title', '')
            self.logger.info(f"Processing item - Number: {number}, Title: {title}")
            
            # Extract content from detail page
            main_content = response.css(self.details_page_main_content_selector).get('').strip()
            cleaned_content = re.sub(r'<[^>]+>', ' ', main_content).strip() if main_content else ''
            
            # Create markdown content
            markdown_content = f"""# {title}

{cleaned_content}
"""
            
            # Save markdown file
            md_filename = f"{self.output_dir}/{number}.md"
            with open(md_filename, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
                
            # Handle attachments
            attachment_links = response.css(self.attachment_links_selector)
            if attachment_links:
                # Create directory for attachments
                attachment_dir = f"{self.output_dir}/{number}"
                if not os.path.exists(attachment_dir):
                    os.makedirs(attachment_dir)
                
                # Handle multiple attachments
                if isinstance(attachment_links, scrapy.selector.Selector):
                    attachment_links = [attachment_links]  # Convert single Selector to list
                
                for index, link in enumerate(attachment_links, start=1):
                    file_url = link.css('::attr(href)').get()
                    
                    file_selector = f":nth-match({self.attachment_links_selector}, {index})"

                    if file_url:
                        filename = link.css('::text').get('').strip()
                        filename = clean_filename(filename)
                        
                        yield scrapy.Request(
                            url=response.url + f"&attachment={index}",
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
                                        selector=file_selector,
                                        save_path=attachment_dir,
                                        file_name=filename
                                    ),
                                ],
                                "errback": self.errback,
                            }
                        )
        except Exception as e:
            self.logger.error(f"Error in parse_details for item {number} - {title}: {e}")
        finally:
            if page and not page.is_closed():
                await page.close()

    async def save_attachment(self, response):
        page = response.meta["playwright_page"]
        filename = response.meta.get("filename")
        
        yield {
            "url": response.url,
            "response_cls": response.__class__.__name__,
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