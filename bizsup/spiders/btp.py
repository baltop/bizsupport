import os
import scrapy
from urllib.parse import urlparse, urljoin, unquote
import mimetypes
import re
import time
from pathlib import Path


class BtpSpider(scrapy.Spider):
    name = "btp"
    OUTPUT_DIR = "btp_output"


    allowed_domains = ["btp.or.kr"]
    start_urls = ["https://www.btp.or.kr/kor/CMS/Board/Board.do?mCode=MN013"]
    
    def __init__(self, *args, **kwargs):
        super(BtpSpider, self).__init__(*args, **kwargs)
        self.page_count = 0
        self.max_pages = 46
        
        # Create output directory
        os.makedirs(self.OUTPUT_DIR, exist_ok=True)
    
    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(
                url=url,
                callback=self.parse,
                meta={"playwright": True}
            )
    
    def parse(self, response):
        self.page_count += 1
        self.logger.info(f"Parsing page {self.page_count}")
        
        # Debug the HTML structure
        self.logger.info(f"HTML Content preview: {response.text[:500]}")
        
        # Try different selectors to find the items
        table_selector = "table.bdListTbl tbody tr"
        
        
        items = []
        items = response.css(table_selector)
        self.logger.info(f"Selector '{table_selector}' found {len(items)} items")
        if not items:
            return
        
        for item in items:
            # Skip notice rows if they exist
            if item.css("td.notice"):
                continue
                
            notice_id = item.css("td:first-child::text").get()
            if notice_id:
                notice_id = notice_id.strip()
            else:
                notice_id = f"btp_{int(time.time())}"
                
            title = item.css("td.subject a::text").get()
            if title:
                title = title.strip()
            else:
                continue  # Skip if no title
                
            detail_url_attr = item.css("td.subject a::attr(href)").get()
            if detail_url_attr:
                detail_url = urljoin(response.url, detail_url_attr)
                self.logger.info(f"Found item: {notice_id} - {title[:30]}... - {detail_url}")
                
                yield scrapy.Request(
                    url=detail_url,
                    callback=self.parse_detail,
                    meta={
                        "playwright": True,
                        "notice_id": notice_id,
                        "title": title
                    }
                )
        
        # 현재 페이지 번호 확인
        current_page = self.page_count
        self.logger.info(f"Current page: {current_page}")
        

        # Handle pagination if we haven't reached max pages
        if self.page_count < self.max_pages:
            next_page = current_page + 1
            next_page_url = self.get_next_page_url(response, current_page)

            self.logger.info(f"Moving to next page: {next_page_url}")
            yield scrapy.Request(
                url=next_page_url,
                callback=self.parse,
                meta={"playwright": True}
            )
    
    def parse_detail(self, response):
        notice_id = response.meta.get('notice_id')
        title = response.meta.get('title')
        
        # Extract content from detail page
        content_div = response.css("div.board-biz-view")
        content = content_div.get()
        
        # Clean and format content
        content = self.clean_html(content)
        
        # Create markdown content
        markdown_content = f"# {title}\n\n{content}"
        
        # Save markdown file
        self.save_markdown(notice_id, markdown_content)
        
        # Extract attachments
        attachments = response.css("div.board-biz-file ul li a")
        
        if attachments:
            # Create directory for attachments if it doesn't exist
            attachment_dir = os.path.join(self.OUTPUT_DIR, f"{notice_id}")
            os.makedirs(attachment_dir, exist_ok=True)
            
            for attachment in attachments:
                file_url = urljoin(response.url, attachment.css("::attr(href)").get())
                file_name = attachment.css("span::text").get().strip()

                # Extract the file extension
                _, ext = os.path.splitext(file_name)
                if ext:
                    ext = ext[:4]  # Keep only the first 3 characters of the extension (including the dot)
                    file_name = f"{os.path.splitext(file_name)[0]}{ext}"  # Reconstruct the file name with the shortened extension




                self.logger.info(f"KHSdir path : {file_url}")
                self.logger.info(f"KHSfile name : {file_name}")
                yield scrapy.Request(
                    url=file_url,
                    callback=self.save_attachment,
                    meta={
                        "playwright": True,
                        "file_name": file_name,
                        "dir_path": attachment_dir
                    }
                )
    
    def save_attachment(self, response):

        dir_path = response.meta.get("dir_path")
        file_name = response.meta.get("file_name")


        # Handle Korean filename if needed
        file_name = unquote(file_name)
        self.logger.info(f"unquote file name : {file_name}")
        
        # Get file extension from Content-Type header or keep original
        content_type = response.headers.get('Content-Type', b'').decode('utf-8', errors='ignore').split(';')[0]
        extension = mimetypes.guess_extension(content_type)
        
        if extension:
            # Only add extension if it doesn't already have one
            if not os.path.splitext(file_name)[1]:
                file_name = f"{file_name}{extension}"
        
        # Save file
        file_path = os.path.join(dir_path, file_name)
        with open(file_path, 'wb') as f:
            f.write(response.body)
            
        self.logger.info(f"Saved attachment: {file_path}")
    
    def save_markdown(self, notice_id, content):
        filename = os.path.join(self.OUTPUT_DIR, f"{notice_id}.md")
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        self.logger.info(f"Saved markdown: {filename}")
    
    def clean_html(self, html_content):
        if not html_content:
            return ""
        
        # Remove HTML tags but preserve line breaks
        text = re.sub(r'<br\s*/?>', '\n', html_content)
        text = re.sub(r'<p[^>]*>', '\n\n', text)
        text = re.sub(r'</p>', '', text)
        text = re.sub(r'<div[^>]*>', '\n', text)
        text = re.sub(r'</div>', '\n', text)
        text = re.sub(r'<li[^>]*>', '- ', text)
        text = re.sub(r'</li>', '\n', text)
        text = re.sub(r'<[^>]+>', '', text)
        
        # Clean up extra whitespace
        text = re.sub(r'\n\s+\n', '\n\n', text)
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        return text.strip()


    
    def get_next_page_url(self, response, current_page):
        """
        다음 페이지 URL 생성
        """
        # 다음 페이지 번호
        next_page = current_page + 1
        
        # 기본 URL (쿼리 스트링 제외)
        base_url = response.url.split('?')[0]
        
        # 현재 URL의 모든 매개변수 유지하되 page만 변경
        params = {}
        if '?' in response.url:
            query_string = response.url.split('?')[1]
            for param in query_string.split('&'):
                if '=' in param:
                    key, value = param.split('=', 1)
                    params[key] = value
        
        # page 파라미터 업데이트
        params['page'] = str(next_page)
        
        # 쿼리 문자열 구성
        query_parts = [f"{k}={v}" for k, v in params.items()]
        next_page_url = f"{base_url}?{'&'.join(query_parts)}"
        
        return next_page_url