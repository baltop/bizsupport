import scrapy
from scrapy.http import Request
from scrapy_playwright.page import PageMethod

class MySpider(scrapy.Spider):
    name = "myspider"








    def start_requests(self):
        yield Request(
            url="https://www.gbtp.or.kr/user/board.do?bbsId=BBSMSTR_000000000021",
            meta={
                "playwright": True,
                "playwright_include_page": True,
                "playwright_page_methods": [
                    PageMethod("click", "table.tablelist tbody tr:nth-child(1) td.title a"),
                    PageMethod("wait_for_load_state", "domcontentloaded") # Ensures the next page is fully loaded before proceeding
                ],
                "errback": self.errback,
            },
            callback=self.parse,
        )

    async def parse(self, response):
         # Extract data after clicking the link
        page = response.meta["playwright_page"]
        html = await page.content()
        self.logger.info(f"Page content: {html}")
        # Further processing of html content
        await page.close()

    async def errback(self, failure):
        page = failure.request.meta["playwright_page"]
        await page.close()