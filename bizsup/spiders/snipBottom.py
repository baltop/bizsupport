import os
import scrapy
from urllib.parse import urlparse, urljoin, unquote
import mimetypes
import re
import time
import json
from pathlib import Path


class SnipBottomSpider(scrapy.Spider):
    name = "snipBottom"
    allowed_domains = ["snip.or.kr"]
    start_urls = ["https://www.snip.or.kr/SNIP/contents/Business1.do"]
    
    def __init__(self, *args, **kwargs):
        super(SnipBottomSpider, self).__init__(*args, **kwargs)
        self.page_count = 0
        self.max_pages = 3
        self.api_url = "https://www.snip.or.kr/SNIP/biz/getBizList.do"
    
    def start_requests(self):
        # This site uses API calls for data, so we'll make a POST request to the API
        formdata = {
            "currentPageNo": "1",
            "recordCountPerPage": "10",
            "section": "business1"
        }
        
        yield scrapy.FormRequest(
            url=self.api_url,
            formdata=formdata,
            callback=self.parse_api,
            meta={"playwright": True, "page": 1}
        )
    
    def parse_api(self, response):
        self.page_count += 1
        current_page = response.meta.get('page', 1)
        
        try:
            # Parse the JSON response
            data = json.loads(response.text)
            
            if 'list' in data:
                items = data['list']
                
                for item in items:
                    notice_id = str(item.get('bizNo', f"snip_{int(time.time())}"))
                    title = item.get('title', 'No Title')
                    
                    # Get detail page info
                    detail_params = {
                        'bizNo': notice_id
                    }
                    
                    detail_url = "https://www.snip.or.kr/SNIP/contents/Business1Detail.do"
                    
                    yield scrapy.FormRequest(
                        url=detail_url,
                        method='GET',
                        formdata=detail_params,
                        callback=self.parse_detail,
                        meta={
                            "playwright": True,
                            "notice_id": notice_id,
                            "title": title
                        }
                    )
            
            # Handle pagination if we haven't reached max pages
            if self.page_count < self.max_pages:
                next_page = current_page + 1
                
                formdata = {
                    "currentPageNo": str(next_page),
                    "recordCountPerPage": "10",
                    "section": "business1"
                }
                
                yield scrapy.FormRequest(
                    url=self.api_url,
                    formdata=formdata,
                    callback=self.parse_api,
                    meta={"playwright": True, "page": next_page}
                )
                
        except json.JSONDecodeError:
            self.logger.error("Failed to parse JSON response")
    
    def parse_detail(self, response):
        notice_id = response.meta.get('notice_id')
        title = response.meta.get('title')
        
        # Extract content from detail page
        content_div = response.css("div.business-detail__info")
        content = content_div.get()
        
        # Clean and format content
        content = self.clean_html(content)
        
        # Create markdown content
        markdown_content = f"# {title}\n\n{content}"
        
        # Save markdown file
        self.save_markdown(notice_id, markdown_content)
        
        # Extract attachments
        attachments = response.css("div.file-download a")
        
        if attachments:
            # Create directory for attachments if it doesn't exist
            attachment_dir = f"{notice_id}"
            os.makedirs(attachment_dir, exist_ok=True)
            
            for attachment in attachments:
                file_url = urljoin(response.url, attachment.css("::attr(href)").get())
                file_name = attachment.css("::text").get().strip()
                
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
        filename = f"{notice_id}.md"
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