import os
import re
import scrapy
from urllib.parse import urlparse, urljoin, unquote


class BtpSpider(scrapy.Spider):
    name = 'btp'
    allowed_domains = ['btp.or.kr']
    start_urls = ['https://www.btp.or.kr/kor/CMS/Board/Board.do?mCode=MN013']
    base_url = 'https://www.btp.or.kr'
    output_dir = 'output/btp'
    page_count = 0
    max_pages = 3

    def __init__(self, *args, **kwargs):
        super(BtpSpider, self).__init__(*args, **kwargs)
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def parse(self, response):
        self.page_count += 1
        self.logger.info(f'Parsing page {self.page_count}')

        # Extract announcement items
        items = response.css('table.bdListTbl > tbody > tr')
        cur_url = response.url
        # cur_url 에서 ? 찾아서  앞에 있는 부분을 base_url로 설정
        if '?' in cur_url:
            cur_base_url = cur_url.split('?')[0]
        else:
            cur_base_url = cur_url

        
        for item in items:
            # Extract details from the list item
            title = item.css('td.subject p.stitle span.subjectWr::text').get('').strip()
            date = item.css('td.date::text').get('').strip()
            status = item.css('td.state span.status::text').get('').strip()
            period = item.css('td.period::text').get('').strip()
            
            # Get the detail page URL
            detail_url = item.css('td.subject p.stitle a::attr(href)').get()
            if detail_url:
                full_url = urljoin(cur_base_url, detail_url)
                yield scrapy.Request(
                    url=full_url,
                    callback=self.parse_detail,
                    meta={
                        'title': title,
                        'date': date,
                        'status': status,
                        'period': period
                    }
                )
        
        # Check if we should proceed to the next page
        if self.page_count < self.max_pages:
            next_page = response.css('div.bdListPaging div.pagelist a.nextblock::attr(href)').get()
            if next_page:
                next_url = urljoin(self.base_url, next_page)
                yield scrapy.Request(url=next_url, callback=self.parse)

    def parse_detail(self, response):
        # Extract metadata from the response meta
        title = response.meta.get('title', '')
        date = response.meta.get('date', '')
        status = response.meta.get('status', '')
        period = response.meta.get('period', '')
        
        # Get board_seq parameter from URL for unique ID
        url_query = urlparse(response.url).query
        board_seq = None
        for param in url_query.split('&'):
            if 'board_seq=' in param:
                board_seq = param.split('=')[1]
                break
        
        if not board_seq:
            board_seq = f"unknown_{hash(response.url) % 10000}"
        
        # Extract content fields
        main_content = response.css('.board-biz-top .txt-box').get('').strip()
        
        # Extract detailed information
        support_target = self.get_info_content(response, 1)
        support_content = self.get_info_content(response, 2)
        application_method = self.get_info_content(response, 3)
        announcement_period = response.css('.board-biz-info ul li.c2 span.txt::text').get('').strip()
        application_period = response.css('.board-biz-info ul li.date span.txt::text').get('').strip()
        
        # Contact information
        contact_info = ''
        contact_elements = response.css('.board-biz-info ul li.refer .txt *::text').getall()
        if contact_elements:
            contact_info = ' '.join([e.strip() for e in contact_elements if e.strip()])
        
        # Create markdown content
        markdown_content = f"""# {title}

## 기본 정보
- 공고일: {date}
- 상태: {status}
- 기간: {period}
- 공고 기간: {announcement_period}
- 접수 기간: {application_period}

## 지원 대상
{support_target}

## 지원 내용
{support_content}

## 신청 방법
{application_method}

## 문의처
{contact_info}

## 상세 내용
{main_content}
"""
        
        # Save markdown file
        md_filename = f"{self.output_dir}/{board_seq}.md"
        with open(md_filename, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        self.logger.info(f"Saved markdown file: {md_filename}")
        
        # Process attachments
        attachment_links = response.css('.board-biz-file .file-list li a')
        if attachment_links:
            # Create directory for attachments
            attachment_dir = f"{self.output_dir}/{board_seq}"
            if not os.path.exists(attachment_dir):
                os.makedirs(attachment_dir)
            
            for link in attachment_links:
                file_url = link.css('::attr(href)').get()
                if file_url:
                    file_url = urljoin(self.base_url, file_url)
                    filename = link.css('span::text').get('').strip()
                    
                    yield scrapy.Request(
                        url=file_url,
                        callback=self.save_attachment,
                        meta={
                            'attachment_dir': attachment_dir,
                            'filename': filename
                        }
                    )
    
    def get_info_content(self, response, index):
        """Extract content from the info section by index"""
        selector = f'.board-biz-info ul li:nth-child({index}) span.txt::text'
        content = response.css(selector).get('')
        if not content:
            # Try alternative selector
            selector = f'.board-biz-info ul li:nth-child({index}) span.txt *::text'
            content = ' '.join([text.strip() for text in response.css(selector).getall() if text.strip()])
        return content.strip()
    
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