import os
import re
import scrapy
from urllib.parse import urlparse, urljoin, unquote


class JbbaSpider(scrapy.Spider):
    name = 'jbba'
    allowed_domains = ['jbba.kr']
    start_urls = ['https://www.jbba.kr/bbs/board.php?bo_table=sub01_09']
    base_url = 'https://www.jbba.kr'
    output_dir = 'output/jbba'
    page_count = 0
    max_pages = 3

    def __init__(self, *args, **kwargs):
        super(JbbaSpider, self).__init__(*args, **kwargs)
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def parse(self, response):
        self.page_count += 1
        self.logger.info(f'Parsing page {self.page_count}')

        # Extract announcement items from the table
        items = response.css('table tbody tr')
        
        for item in items:
            # Extract details from the list item
            number = item.css('td.td_num::text').get('').strip()
            title = item.css('td.td_subject a::text').get('').strip()
            period = item.css('td:nth-child(3)::text').get('').strip()
            manager = item.css('td:nth-child(4)::text').get('').strip()
            
            # Get the detail page URL
            detail_url = item.css('td.td_subject a::attr(href)').get()
            if detail_url:
                full_url = urljoin(self.base_url, detail_url)
                yield scrapy.Request(
                    url=full_url,
                    callback=self.parse_detail,
                    meta={
                        'number': number,
                        'title': title,
                        'period': period,
                        'manager': manager
                    }
                )
        
        # Check if we should proceed to the next page
        if self.page_count < self.max_pages:
            next_page = response.css('nav.pg_wrap span.pg a.pg_page::attr(href)').getall()
            if next_page and len(next_page) > 0:
                # Get the next page URL
                next_url = urljoin(self.base_url, next_page[0])
                yield scrapy.Request(url=next_url, callback=self.parse)

    def parse_detail(self, response):
        # Extract metadata from the response meta
        number = response.meta.get('number', '')
        title = response.meta.get('title', '')
        period = response.meta.get('period', '')
        manager = response.meta.get('manager', '')
        
        # Extract wr_id parameter from URL to use as unique ID
        url_query = urlparse(response.url).query
        wr_id = None
        for param in url_query.split('&'):
            if 'wr_id=' in param:
                wr_id = param.split('=')[1]
                break
        
        if not wr_id:
            wr_id = f"unknown_{hash(response.url) % 10000}"
        
        # Extract content
        content_section = response.css('section#bo_v_atc')
        main_content = content_section.css('div#bo_v_con').get('') if content_section else ''
        
        # Clean HTML tags if needed
        cleaned_content = re.sub(r'<[^>]+>', ' ', main_content).strip() if main_content else ''
        
        # Create markdown content
        markdown_content = f"""# {title}

## 기본 정보
- 공고 번호: {number}
- 접수 기간: {period}
- 담당자: {manager}

## 상세 내용
{cleaned_content}
"""
        
        # Save markdown file
        md_filename = f"{self.output_dir}/{wr_id}.md"
        with open(md_filename, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        self.logger.info(f"Saved markdown file: {md_filename}")
        
        # Process attachments
        attachment_links = response.css('section#bo_v_file ul li')
        if attachment_links:
            # Create directory for attachments
            attachment_dir = f"{self.output_dir}/{wr_id}"
            if not os.path.exists(attachment_dir):
                os.makedirs(attachment_dir)
            
            for link in attachment_links:
                file_url = link.css('a::attr(href)').get()
                if file_url:
                    file_url = urljoin(self.base_url, file_url)
                    filename = link.css('a strong::text').get('').strip()
                    
                    yield scrapy.Request(
                        url=file_url,
                        callback=self.save_attachment,
                        meta={
                            'attachment_dir': attachment_dir,
                            'filename': filename
                        }
                    )
    
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