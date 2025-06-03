import scrapy
from scrapy_playwright.page import PageMethod

class TestGdtpSpider(scrapy.Spider):
    name = "test_gdtp"
    start_urls = ['https://www.gdtp.or.kr/board/notice']
    
    custom_settings = {
        'DOWNLOAD_HANDLERS': {
            'http': 'scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler',
            'https': 'scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler',
        },
        'TWISTED_REACTOR': 'twisted.internet.asyncioreactor.AsyncioSelectorReactor',
    }

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
        page = response.meta["playwright_page"]
        
        # HTML 구조 확인
        html_content = await page.content()
        print("="*50)
        print("HTML CONTENT SAMPLE:")
        print("="*50)
        
        # 공고 목록 부분 찾기
        import re
        notice_section = re.search(r'<div[^>]*class="[^"]*bbs-list[^"]*"[^>]*>.*?</div>', html_content, re.DOTALL)
        if notice_section:
            print("FOUND BBS-LIST SECTION:")
            print(notice_section.group(0)[:1000])
        else:
            print("BBS-LIST SECTION NOT FOUND")
            
        # 다른 방법으로 찾기
        table_section = re.search(r'<table[^>]*>.*?</table>', html_content, re.DOTALL)
        if table_section:
            print("FOUND TABLE SECTION:")
            print(table_section.group(0)[:1000])
        else:
            print("TABLE SECTION NOT FOUND")
            
        # 제목 링크들 찾기
        title_links = re.findall(r'<a[^>]*href="[^"]*post/\d+[^"]*"[^>]*>([^<]+)</a>', html_content)
        print(f"FOUND {len(title_links)} TITLE LINKS:")
        for i, title in enumerate(title_links[:5]):
            print(f"{i+1}. {title}")
            
        await page.close()