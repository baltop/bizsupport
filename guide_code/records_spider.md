

```python
import playwright.async_api
import scrapy
from scrapy_playwright.page import PageMethod

# from ..item_loaders import RecordLoader
# from ..items import RecordItem


class RecordsSpider(scrapy.Spider):
    name = "records_spider"

    def start_requests(self):
        yield scrapy.Request(
            'https://reactstorefront.vercel.app/default-channel/en-US/category/records/',
            meta=dict(
                playwright=True,
                playwright_include_page=True,
                playwright_page_methods=[
                    PageMethod('wait_for_selector', 'button.relative.text-base')
                ]
            ),
            callback=self.parse_first
        )

    async def parse_first(self, response: scrapy.http.Response):
        page: playwright.async_api.Page = response.meta["playwright_page"]
        while True:
            button = page.locator('button.relative.text-base')
            if (await button.count()) == 0:
                break
            await button.click()
            for url in await page.locator('a').all():
                href = await url.get_attribute('href')
                if href.startswith('/default-channel/en-US/products/'):
                    yield scrapy.Request(
                        response.urljoin(href),
                        callback=self.parse_item
                    )

    def parse_item(self, response: scrapy.http.Response):
        loader = RecordLoader(item=RecordItem(), response=response)
        loader.add_value("url", response.url)
        loader.add_css('name', 'h1[data-testid="productName"]::text')

        prices = response.css('div.flex.flex-row.gap-2.w-full.font-semibold.text-md>div:nth-child(2)::text').getall()
        loader.add_value("cd_usd_price", prices[0])
        loader.add_value("vinyl_usd_price", prices[1])

        attributes = []
        for attribute in response.css('div[class="grid grid-cols-2"]>div:nth-child(even)'):
            text_of_attribute = ' '.join(attribute.css("p::text").getall())
            attributes.append(text_of_attribute)

        loader.add_value("release_type", attributes[0])
        loader.add_value("artist", attributes[1])
        loader.add_value("artist_page", attributes[2])
        loader.add_value("genre", attributes[3])
        loader.add_value("release_year", attributes[4])
        loader.add_value("label", attributes[5])
        loader.add_value("country", attributes[6])

        return loader.load_item()

```


```python
from scrapy.spiders import Spider
from scrapy.http import Request
from scrapy.selector import Selector

class Spider(Spider): 
    name = "example_quotes"
    allowed_domain = []
    start_urls = ["https://quotes.toscrape.com/page/1/"]
    page_num = 1

    custom_settings={
        'PLAYWRIGHT_PROCESS_REQUEST_HEADERS' : None,
    }

    def start_requests(self):
        yield Request(
            url=self.start_urls[0],
            meta={
                "playwright" : True,
                "playwright_include_page" : True,
            },
            callback=self.parse,
            errback=self.errback
        )
    
    async def parse(self, response):
        # get the page from the response
        page = response.meta["playwright_page"]
        
        # some wait method to wait for 
        # the desired load state 
        await page.wait_for_load_state()

        # get page content
        content = await page.content()
        # transform into a Selector
        selector = Selector(text=content)

        # extract some data
        quotes = await page.locator('div.quote').all()
        for quote in quotes:
            # get a Locator
            button = quote.get_by_text('(about)')
            # make an action
            await button.click()
            # wait method
            await page.wait_for_timeout(3*1000)

            # extract some data
            born_date = await page.locator('.author-born-date').inner_text()
            print('\n ######################################################\n',
                'The author of this quote was born on: ', born_date, '\n',
                '######################################################\n')

            # go back to main page
            await page.go_back()
            await page.wait_for_timeout(3*1000)

        # get next url from the content
        next_url = selector.xpath('.//li[@class="next"]//@href').get()

        if next_url :
            # yield a new Request using the same page
            next_url = "https://quotes.toscrape.com" + next_url
            yield Request(
                url= next_url,
                meta={
                    "playwright" : True,
                    "playwright_include_page" : True,
                    "playwright_page": page,
                    },
                callback=self.parse,
                errback=self.errback
            )
        else:
            # close the page at the end
            await page.close()

    async def errback(self, failure):
        page = failure.request.meta.get("playwright_page")
        if page is not None:
            await page.close()
            await page.context.close()
    
```

```python
from scrapy.spiders import Spider
from scrapy.http import Request
from scrapy.selector import Selector

class Spider(Spider): 
    name = "my_spider"
    allowed_domain = []
    start_urls = ["https://example.com"]

    cookies = [
        {"name": "cookie_name_1", "value":"cookie_value_1","domain": "https://example.com" ,"path": "/" },
        {"name": "cookie_name_2", "value":"cookie_value_2","domain": "https://example.com" ,"path": "/" },
    ]

    def should_abort_request(request):
        return (
            request.resource_type == "image"
            or "google" in request.url
            or ".jpg" in request.url 
            or ".png" in request.url 
            or ".css" in request.url # careful with this option
        )

    custom_settings={
        'PLAYWRIGHT_ABORT_REQUEST' : should_abort_request,
        'PLAYWRIGHT_PROCESS_REQUEST_HEADERS' : None,
        'PLAYWRIGHT_CONTEXTS': {
            'context_cookies':{
                'storage_state': {
                        'cookies': cookies,
                },
            },
        }
    }

    def start_requests(self):
        for url in self.start_urls:
            yield Request(
                url=url,
                meta={
                    "playwright" : True,
                    "playwright_include_page" : True,
                    "playwright_context": "context_cookies",
                },
                callback=self.parse,
                errback=self.errback
            )
    
    async def parse(self):
        # get the page from the response
        page = response.meta["playwright_page"]

        # see if cookies were received
        storage_state = await page.context.storage_state()
        print('Page cookies: ', storage_state['cookies'])
        
        # some wait method to wait for 
        # the desired load state 
        await page.wait_for_load_state()

        # get page content
        content = await page.content()
        # transform into a Selector
        selector = Selector(text=content)
        # extract some data
        data1 = selector.xpath('.//a[@class="data"]/text()')
        
        # extract same data using Playwright
        data2 = await page.locator(".data").inner_text()
        
        # get a Locator
        button = page.get_by_role("button")
        # make an action
        await button.click()
        # wait method
        await page.wait_for_timeout(3*1000)

        ##################
        # do other stuff #
        ##################
        
        # some other dynamic actions
        await page.go_back()
        await page.wait_for_timeout(3*1000)

        # close the page and the context
        
        await page.close()
        await page.context.close()

    async def errback(self, failure):
        page = failure.request.meta.get("playwright_page")
        if page is not None:
            await page.close()
            await page.context.close()
    


```

