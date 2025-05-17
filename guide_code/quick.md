
## some useful code snippets for quick reference


# url parsing

```python
        # Extract wr_id parameter from URL to use as unique ID
        url_query = urlparse(response.url).query
        wr_id = None
        for param in url_query.split('&'):
            if 'wr_id=' in param:
                wr_id = param.split('=')[1]
                break
        
        if not wr_id:
            wr_id = f"unknown_{hash(response.url) % 10000}"
```


# filename extraction

```python
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
```


# file download

```python
    def start_requests(self):
        yield Request(url="https://example.org", meta={"playwright": True})
        yield Request(
            url="https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf",
            meta={"playwright": True},
        )

    def parse(self, response, **kwargs):
        if filename := response.meta.get("playwright_suggested_filename"):
            (Path(__file__).parent / filename).write_bytes(response.body)
        yield {
            "url": response.url,
            "response_cls": response.__class__.__name__,
            "first_bytes": response.body[:60],
            "filename": filename,
        }
```


# current url

```python
        cur_url = response.url
        # cur_url 에서 ? 찾아서  앞에 있는 부분을 base_url로 설정
        if '?' in cur_url:
            cur_base_url = cur_url.split('?')[0]
        else:
            cur_base_url = cur_url
```


# inpage playwright click

```python
    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(
                url=url,
                callback=self.parse,
                meta={
                    "playwright": True,
                    "playwright_include_page": True,
                    "playwright_page_methods": [
                        PageMethod("wait_for_selector", "table.list")
                    ]
                }
            )

    async def parse(self, response):
        self.page_count += 1
        self.logger.info(f'Parsing page {self.page_count}')
        
        page = response.meta["playwright_page"]
        
        try:
            # Extract announcement items from the table
            items = response.css('table.list.fixed tbody tr')
            
            for item in items:
                
                # Extract details from the list item
                number = item.css('td:nth-child(1)::text').get('').strip()
                title = item.css('td.subject a::text').get('').strip()

                # Get the detail page URL
                detail_url = item.css('td.subject a::attr(href)').get()
                
                if detail_url:
                    # Click on the link to open the detail page in a new tab
                    await page.click(f'text="{title}"')
                    # Wait for the new page to open
                    new_page = await page.context.wait_for_event('page')
                    # Wait for the page to load
                    await new_page.wait_for_load_state('networkidle')
                    
                    # Extract content from the new page
                    content_html = await new_page.content()
                    # Create a new response object
                    detail_response = response.replace(body=content_html.encode(), url=new_page.url)
                    
                    yield self.parse_detail(detail_response, {
                        'number': number,
                        'title': title
                    })
                    
                    # Close the detail page
                    await new_page.close()
            
            # Check if we should proceed to the next page
            if self.page_count < self.max_pages:
                # Find the next page button
                next_page = self.page_count + 1
                if next_page:
                    next_url = "https://itp.or.kr/intro.asp?tmid=13&PageNum={next_page}"
                    yield scrapy.Request(
                        url=next_url,
                        callback=self.parse,
                        meta={
                            "playwright": True,
                            "playwright_include_page": True,
                            "playwright_page_methods": [
                                PageMethod("wait_for_selector", "table.list")
                            ]
                        }
                    )
                    
        except Exception as e:
            self.logger.error(f"Error occurred: {e}")
            self.logger.error(f"Response URL: {response.url}")
            self.logger.error(f"Response body: {response.text}")
            self.logger.error(f"Meta data: {response.meta}")
        finally:
            await page.close()
```


# nth pseudo class

```python
await page.locator(':nth-match(:text("Buy"), 3)').click();
```


