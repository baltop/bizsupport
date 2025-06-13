import os
import scrapy
from urllib.parse import urlparse, urljoin, unquote
import mimetypes
import re
from pathlib import Path
import time


class SeoultpSpider(scrapy.Spider):
    name = "seoultp"
    allowed_domains = ["seoultp.or.kr"]
    start_urls = ["https://www.seoultp.or.kr/user/nd19746.do"]
    
    def __init__(self, *args, **kwargs):
        super(SeoultpSpider, self).__init__(*args, **kwargs)
        self.page_count = 0
        self.max_pages = 5
        # Create output directory
        self.output_dir = "output/seoultp"
        os.makedirs(self.output_dir, exist_ok=True)
    
    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(
                url=url,
                callback=self.parse,
                meta={"playwright": True}
            )
    
    def parse(self, response):
        self.page_count += 1
        
        # Extract items from the list
        items = response.css("table.board-list tbody tr")
        
        for item in items:
            notice_id = item.css("td:nth-child(1)::text").get().strip()
            if not notice_id:
                notice_id = f"공지_{int(time.time())}"

            title = item.css("td.left a::text").get().strip()
            # td.subject a::attr(onclick)
            self.logger.info(f"title : '{title}'")

            # Handle JavaScript link for detail page
            onclick_attr = item.css("td.left a::attr(href)").get()
            self.logger.info(f"onclick_attr : '{onclick_attr}'")

            if onclick_attr:
                # Extract parameters from JavaScript function
                # js_params = re.search(r"goBoardView\('(\d+)'\)", onclick_attr)
                
                js_params = re.search(r"goBoardView\('[^']*','[^']*','([^']+)'\)", onclick_attr)

                if js_params:
                    param1 = js_params.group(1)
                    
                    detail_url = f"https://www.seoultp.or.kr/user/nd19746.do?View&pageLS=10&pageST=SUBJECT&pageSV=&page=5&pageSC=SORT_ORDER&pageSO=DESC&dmlType=&boardNo={param1}&menuCode=www"

                    self.logger.info(f"Detail URL: {detail_url}")
                    
                    yield scrapy.Request(
                        url=detail_url,
                        callback=self.parse_detail,
                        meta={
                            "playwright": True,
                            "notice_id": notice_id,
                            "title": title
                        }
                    )
        
        # Handle pagination if we haven't reached max pages
        if self.page_count < self.max_pages:
            # Look for next page link

            current_page = self.page_count
            next_page = current_page + 1
            next_page_url =  f"https://www.seoultp.or.kr/user/nd19746.do?pageLS=10&pageST=SUBJECT&pageSV=&page={next_page}&pageSC=SORT_ORDER&pageSO=DESC&dmlType=SELECT&boardNo=&menuCode=www"
           
            yield scrapy.Request(
                url=next_page_url,
                callback=self.parse,
                meta={"playwright": True}
            )

    
    def parse_detail(self, response):
        notice_id = response.meta.get('notice_id')
        title = response.meta.get('title')
        
        # Extract content from detail page
        content_div = response.css("div#contents")
        content = content_div.get()
        
        # Clean and format content
        content = self.clean_html(content)
        
        # Create markdown content
        markdown_content = f"# {title}\n\n{content}"
        
        # Save markdown file
        self.save_markdown(notice_id, markdown_content)
        
        # Extract attachments
        attachments = response.css("ul.downfile-list li a")
        
        if attachments:
            # Create directory for attachments if it doesn't exist
            attachment_dir = os.path.join(self.output_dir, f"{notice_id}")
            os.makedirs(attachment_dir, exist_ok=True)
            
            for attachment in attachments:
                file_selector = attachment.css("::attr(onclick)").get()
                # file_name = attachment.css("::text").get().strip()
                file_name = attachment.css("::text").get().strip()

                
                file_match = re.search(r"attachfileDownload\('([^']*)','([^']*)'\)", file_selector)
                
                if file_match:
                    file_urlseg = file_match.group(1)
                    file_id = file_match.group(2)
                    file_url = file_urlseg + "?attachNo=" + file_id
                    file_url = urljoin(response.url, file_url)
                    
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
        
        # # Get file extension from Content-Type header or keep original
        # content_type = response.headers.get('Content-Type', b'').decode('utf-8', errors='ignore').split(';')[0]
        # extension = mimetypes.guess_extension(content_type)
        
        # if extension:
        #     # Only add extension if it doesn't already have one
        #     if not os.path.splitext(file_name)[1]:
        #         file_name = f"{file_name}{extension}"
        
        # Save file
        file_path = os.path.join(dir_path, file_name)
        with open(file_path, 'wb') as f:
            f.write(response.body)
            
        self.logger.info(f"Saved attachment: {file_path}")
    
    def save_markdown(self, notice_id, content):
        filename = os.path.join(self.output_dir, f"{notice_id}.md")
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