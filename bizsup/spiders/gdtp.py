# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import Request
from scrapy_playwright.page import PageMethod
import os
import re
import asyncio
import time
from urllib.parse import urlparse, urlunparse
from bizsup.utils import clean_filename, click_and_handle_download, create_output_directory

class GdtpSpider(scrapy.Spider):
    name = "gdtp"
    allowed_domains = ['gdtp.or.kr']
    start_urls = ['https://www.gdtp.or.kr/board/notice']
    base_url = 'https://www.gdtp.or.kr'
    output_dir = 'output/gdtp'
    page_count = 0
    max_pages = 6

    custom_settings = {
        'DOWNLOAD_HANDLERS': {
            'http': 'scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler',
            'https': 'scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler',
        },
        'TWISTED_REACTOR': 'twisted.internet.asyncioreactor.AsyncioSelectorReactor',
        'PLAYWRIGHT_ABORT_REQUEST': lambda req: req.resource_type == "image",
    }

    def __init__(self, *args, **kwargs):
        super(GdtpSpider, self).__init__(*args, **kwargs)
        create_output_directory(self.output_dir)

    def start_requests(self):
        yield scrapy.Request(
            url=self.start_urls[0],
            meta={
                "playwright": True,
                "playwright_include_page": True,
                "playwright_page_methods": [
                    PageMethod("wait_for_load_state", "domcontentloaded"),
                ]
            },
            callback=self.parse
        )

    async def parse(self, response):
        self.page_count += 1
        page = response.meta["playwright_page"]
        
        try:
            # 공고 링크들 직접 추출
            notice_links = response.css("a[href*='/post/']")
            self.logger.info(f"Found {len(notice_links)} notice links on page {self.page_count}")
            
            for index, link in enumerate(notice_links, start=1):
                href = link.css("::attr(href)").get()
                title = link.css("::text").get()
                
                if href and title:
                    # URL이 상대경로인 경우 절대경로로 변환
                    if href.startswith('/'):
                        detail_url = self.base_url + href
                    else:
                        detail_url = href
                    
                    # 번호는 URL에서 추출
                    post_id = href.split('/')[-1] if '/' in href else str(int(time.time()) + index)
                    
                    self.logger.info(f"Processing: {post_id} - {title.strip()}")
                    
                    yield Request(
                        url=detail_url,
                        meta={
                            "playwright": True,
                            "playwright_include_page": True,
                            "playwright_page_methods": [
                                PageMethod("wait_for_load_state", "domcontentloaded"),
                            ],
                            "number": post_id,
                            "title": title.strip(),
                        },
                        callback=self.parse_details,
                        dont_filter=True,
                    )
            
            # 페이지네이션 처리
            if self.page_count < self.max_pages:
                next_page = self.page_count + 1
                next_page_url = f"https://www.gdtp.or.kr/board/notice?&page={next_page}"
                self.logger.info(f"Moving to next page: {next_page_url}")
                
                yield scrapy.Request(
                    url=next_page_url,
                    callback=self.parse,
                    meta={
                        "playwright": True,
                        "playwright_include_page": True,
                        "playwright_page_methods": [
                            PageMethod("wait_for_load_state", "domcontentloaded"),
                        ]
                    }
                )
        except Exception as e:
            self.logger.error(f"Error in parse: {e}")
        finally:
            if page and not page.is_closed():
                await page.close()

    async def parse_details(self, response):
        page = response.meta["playwright_page"]
        number = response.meta.get('number', '')
        title = response.meta.get('title', '')
        
        try:
            self.logger.info(f"Parsing details for: {number} - {title}")
            
            # 메인 콘텐츠 추출 - 여러 선택자를 시도
            main_content = ""
            content_selectors = [
                "div.bbs-content",
                "div#content", 
                "article",
                ".content",
                "main"
            ]
            
            for selector in content_selectors:
                content_element = response.css(selector)
                if content_element:
                    main_content = content_element.get()
                    break
            
            if main_content:
                # HTML 태그 제거하여 텍스트만 추출
                cleaned_content = re.sub(r'<[^>]+>', ' ', main_content)
                # 여러 공백을 하나로 정리
                cleaned_content = re.sub(r'\s+', ' ', cleaned_content).strip()
            else:
                # 모든 텍스트 추출
                all_text = response.css('body *::text').getall()
                cleaned_content = ' '.join([text.strip() for text in all_text if text.strip()])
            
            # 마크다운 형식으로 저장
            markdown_content = f"""# {title}

## 공고 내용
{cleaned_content}

---
URL: {response.url}
작성일: {time.strftime('%Y-%m-%d %H:%M:%S')}
"""
            
            # 파일명 정리
            safe_filename = clean_filename(f"{number}_{title}")
            if not safe_filename:
                safe_filename = str(number)
            
            md_filename = f"{self.output_dir}/{safe_filename}.md"
            
            with open(md_filename, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            
            self.logger.info(f"Saved markdown file: {md_filename}")
            
            # 첨부파일 처리 - 여러 패턴 시도
            attachment_selectors = [
                "p a[href*='javascript:file_download']",
                "a[href*='download']", 
                "a[href*='.pdf']",
                "a[href*='.hwp']",
                "a[href*='.zip']",
                "a[href*='.doc']"
            ]
            
            attachment_links = []
            for selector in attachment_selectors:
                links = response.css(selector)
                if links:
                    attachment_links.extend(links)
            
            if attachment_links:
                attachment_dir = f"{self.output_dir}/{safe_filename}_attachments"
                if not os.path.exists(attachment_dir):
                    os.makedirs(attachment_dir)
                
                for index, link in enumerate(attachment_links, start=1):
                    file_url = link.css('::attr(href)').get()
                    if file_url:
                        filename_text = link.css('::text').get('') or f"attachment_{index}"
                        # 파일명에서 확장자 추출
                        if '.' in filename_text:
                            filename = clean_filename(filename_text)
                        else:
                            filename = clean_filename(f"attachment_{index}")
                        
                        download_url = response.urljoin(file_url) if not file_url.startswith('http') else file_url
                        
                        yield scrapy.Request(
                            url=download_url,
                            callback=self.save_attachment,
                            dont_filter=True,
                            meta={
                                'attachment_dir': attachment_dir,
                                'filename': filename,
                                "playwright": True,
                                "playwright_include_page": True,
                            }
                        )
        except Exception as e:
            self.logger.error(f"Error in parse_details for {number} - {title}: {e}")
        finally:
            if page and not page.is_closed():
                await page.close()

    async def save_attachment(self, response):
        page = response.meta.get("playwright_page")
        attachment_dir = response.meta.get('attachment_dir')
        filename = response.meta.get('filename')
        
        try:
            if response.body:
                file_path = os.path.join(attachment_dir, filename)
                with open(file_path, 'wb') as f:
                    f.write(response.body)
                self.logger.info(f"Saved attachment: {file_path}")
            else:
                self.logger.warning(f"Empty file content for: {filename}")
        except Exception as e:
            self.logger.error(f"Error saving attachment {filename}: {e}")
        finally:
            if page and not page.is_closed():
                await page.close()

    async def errback(self, failure):
        page = failure.request.meta.get("playwright_page")
        self.logger.error(f"Request failed: {failure.request.url}")
        self.logger.error(f"Error: {failure.value}")
        if page and not page.is_closed():
            await page.close()