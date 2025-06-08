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

class JejutpSpider(scrapy.Spider):
    name = "jejutp"
    allowed_domains = ['jejutp.or.kr']
    start_urls = ['https://www.jejutp.or.kr/board/business']
    base_url = 'https://www.jejutp.or.kr'
    output_dir = 'output/jejutp'
    page_count = 0
    max_pages = 2
    items_selector = "table.AW_bbs_table tbody tr"

    item_title_selector = "td.text-left a::text"
    click_selector = "table.AW_bbs_table tbody tr td.text-left a"

    details_page_main_content_selector = "div.board_area"
    attachment_links_selector = "div.py-3.border-top.border-bottom div p a"
    
    next_page_url = "https://www.jejutp.or.kr/board/business/list?keyword=&page={next_page}&size=30&businessDiv="
    
    custom_settings = {
        "PLAYWRIGHT_ABORT_REQUEST": abort_request,
    }

    def __init__(self, *args, **kwargs):
        super(JejutpSpider, self).__init__(*args, **kwargs)
        create_output_directory(self.output_dir)

    async def start(self):
        yield scrapy.Request(
            url=self.start_urls[0],
            meta={
                "playwright": True,
                "playwright_include_page": True,
                "playwright_page_methods": [
                    PageMethod("wait_for_selector", self.click_selector),
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
                
                number = item.css('td:nth-child(1)::text').get('').strip()
                if not number:
                    number = str(int(time.time()))
                    
                title = item.css(self.item_title_selector).get('').strip()
                title_selector = f":nth-match({self.click_selector}, {index})"

                yield Request(
                    url= current_url,
                    meta={
                        "playwright": True,
                        "playwright_include_page": True,
                        "playwright_page_methods": [
                            PageMethod("click", title_selector),
                            PageMethod("wait_for_selector", self.details_page_main_content_selector),
                            # div.py-3.border-top.border-bottom
                            PageMethod("wait_for_selector", "div.py-3.border-top.border-bottom"),
                            # PageMethod("wait_for_load_state", "domcontentloaded"),
                        ],
                        "errback": self.errback,
                        "number": number,
                        "title": title,
                    },
                    callback=self.parse_details,
                    dont_filter=True,
                )
                
        except Exception as e:
            self.logger.error("parse"+ number + " " + title)
            self.logger.error(f"Error occurred: {e}")
            self.logger.error(f"Response URL: {response.url}")
            self.logger.error(f"Meta data: {response.meta}")
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
                    PageMethod("wait_for_selector", self.click_selector),
                ],
            })

    async def parse_details(self, response):
        try:
            page = response.meta["playwright_page"]
            
            number = response.meta.get('number', '')
            title = response.meta.get('title', '')
            self.logger.info(f"Number: {number}, Title: {title}")
            
            main_content = response.css(self.details_page_main_content_selector).get('').strip()
            cleaned_content = re.sub(r'<[^>]+>', ' ', main_content).strip() if main_content else ''
            
            markdown_content = f"""# {title}
            {cleaned_content}
            """
            
            md_filename = f"{self.output_dir}/{number}.md"
            with open(md_filename, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
                
            current_url = response.url
            parsed_url = urlparse(current_url)
            url_without_params = urlunparse(parsed_url._replace(query=''))
            self.logger.info(f"url_without_params: +++++++++++++++++++++++++++++++++++++ {url_without_params}")

            attachment_links = response.css(self.attachment_links_selector)
            if attachment_links:
                attachment_dir = f"{self.output_dir}/{number}"
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
            self.logger.error("parse_details" + number + " " + title)
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