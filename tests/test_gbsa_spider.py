import pytest
from bizsup.spiders.gbsa import GbsaSpider
from scrapy.http import HtmlResponse, Request
from scrapy_playwright.page import PageMethod
# from playwright.async_api import Page # Not strictly required if not type checking Page
import asyncio
import time # For potential use in number generation if main logic changes
import re # For markdown cleaning
from unittest.mock import patch, mock_open

from bizsup.utils import click_and_handle_download, clean_filename

# Mock Playwright Page class for testing
class MockPlaywrightPage:
    def __init__(self):
        self._is_closed = False
        self.url = "http://mock.url" # Add a url attribute

    async def close(self):
        self._is_closed = True
        # print("MockPlaywrightPage closed in test") # For debugging
        await asyncio.sleep(0) 

    def is_closed(self):
        return self._is_closed
    
    async def query_selector(self, selector): # Add if spider uses page.query_selector
        # Return a dummy element or None based on test needs
        return True # Or a more sophisticated mock if element properties are accessed

    async def wait_for_selector(self, selector, **kwargs): # Add if spider uses this
        await asyncio.sleep(0)
        return True
    
    async def wait_for_load_state(self, state, **kwargs): # Add if spider uses this
        await asyncio.sleep(0)
        return True

# Existing test_spider_instantiation
def test_spider_instantiation():
    spider = GbsaSpider()
    assert spider.name == "gbsa"
    assert "gbsa.or.kr" in spider.allowed_domains

@pytest.mark.asyncio
async def test_parse_method_yields_requests():
    spider = GbsaSpider()
    spider.max_pages = 1 
    spider.page_count = 0

    mock_html_content = """
    <html>
        <body>
            <table class="bbs-list">
                <tbody>
                    <tr>
                        <td>1</td>
                        <td class="align_left"><a href="http://example.com/item1">Test Item 1</a></td>
                        <td>Date 1</td>
                        <td>Views 1</td>
                    </tr>
                    <tr>
                        <td>2</td>
                        <td class="align_left"><a href="http://example.com/item2">Test Item 2</a></td>
                        <td>Date 2</td>
                        <td>Views 2</td>
                    </tr>
                </tbody>
            </table>
            <div class="pagination"></div>
        </body>
    </html>
    """
    mock_page = MockPlaywrightPage()
    mock_url = spider.start_urls[0]
    mock_response = HtmlResponse(
        url=mock_url,
        body=mock_html_content,
        encoding='utf-8',
        meta={"playwright_page": mock_page}
    )

    requests = []
    async for req_or_item in spider.parse(mock_response):
        if isinstance(req_or_item, Request):
            requests.append(req_or_item)

    assert len(requests) == 2, f"Expected 2 item requests, got {len(requests)}"
    expected_items_data = [
        {"number": "1", "title": "Test Item 1"},
        {"number": "2", "title": "Test Item 2"},
    ]

    for i, req in enumerate(requests):
        assert isinstance(req, Request)
        assert req.callback == spider.parse_details
        assert req.url == mock_url 
        assert req.meta.get("playwright") is True
        assert req.meta.get("playwright_include_page") is True
        page_methods = req.meta["playwright_page_methods"]
        assert len(page_methods) == 2
        click_method = page_methods[0]
        assert isinstance(click_method, PageMethod)
        assert click_method.method == "click"
        expected_click_selector = f":nth-match(td.align_left a, {i+1})"
        assert click_method.args[0] == expected_click_selector
        wait_method = page_methods[1]
        assert isinstance(wait_method, PageMethod)
        assert wait_method.method == "wait_for_load_state"
        assert wait_method.args[0] == "domcontentloaded"
        assert req.meta.get("title") == expected_items_data[i]["title"]
        assert req.meta.get("number") == expected_items_data[i]["number"]
        assert req.errback == spider.errback
        assert req.dont_filter is True
    assert mock_page.is_closed(), "Playwright page was not closed at the end of parse"

@pytest.mark.asyncio
async def test_parse_pagination():
    spider = GbsaSpider()
    spider.page_count = 0
    spider.max_pages = 2

    mock_html_content_page1 = """
    <html><body>
        <table class="bbs-list"><tbody>
            <tr><td>1</td><td class="align_left"><a href="#">Item 1 Page 1</a></td></tr>
        </tbody></table>
        <div class="pagination"><a href="#" onclick="javascript:searchPage('2');">Next</a></div>
    </body></html>"""
    mock_page = MockPlaywrightPage()
    response_page1 = HtmlResponse(
        url=spider.start_urls[0], body=mock_html_content_page1, encoding='utf-8',
        meta={"playwright_page": mock_page}
    )
    requests = []
    async for req_or_item in spider.parse(response_page1):
        if isinstance(req_or_item, Request): requests.append(req_or_item)
    assert len(requests) == 2
    item_request_found = any(r.callback == spider.parse_details for r in requests)
    pagination_request_found = any(r.callback == spider.parse for r in requests)
    assert item_request_found
    assert pagination_request_found
    for req in requests:
        if req.callback == spider.parse:
            assert req.meta.get("playwright") is True
            page_methods = req.meta.get("playwright_page_methods", [])
            assert any(pm.method == "click" and pm.args[0] == "div.pagination a[onclick*='searchPage(\\'2\\')']" for pm in page_methods)
    assert spider.page_count == 1

@pytest.mark.asyncio
async def test_spider_errback_closes_page():
    spider = GbsaSpider()
    mock_page = MockPlaywrightPage()
    mock_request = Request(url="http://example.com", meta={"playwright_page": mock_page})
    class MockFailure:
        def __init__(self, request): self.request = request; self.value = "Mocked error"
    mock_failure = MockFailure(mock_request)
    await spider.errback(mock_failure)
    assert mock_page.is_closed() is True

@pytest.mark.asyncio
async def test_parse_no_items_found():
    spider = GbsaSpider()
    spider.max_pages = 1; spider.page_count = 0
    mock_html_content_no_items = "<html><body><table class='bbs-list'><tbody></tbody></table></body></html>"
    mock_page = MockPlaywrightPage()
    mock_response = HtmlResponse(
        url=spider.start_urls[0], body=mock_html_content_no_items, encoding='utf-8',
        meta={"playwright_page": mock_page}
    )
    requests = []
    async for req_or_item in spider.parse(mock_response):
        if isinstance(req_or_item, Request): requests.append(req_or_item)
    assert len(requests) == 0
    assert spider.page_count == 1 
    assert mock_page.is_closed()

@pytest.mark.asyncio
async def test_parse_item_number_fallback(monkeypatch):
    spider = GbsaSpider()
    spider.max_pages = 1; spider.page_count = 0
    mock_html_content_no_number = """
    <html><body><table class="bbs-list"><tbody>
        <tr><td></td><td class="align_left"><a href="#">Test Item No Number</a></td></tr>
    </tbody></table></body></html>"""
    mock_page = MockPlaywrightPage()
    mock_response = HtmlResponse(
        url=spider.start_urls[0], body=mock_html_content_no_number, encoding='utf-8',
        meta={"playwright_page": mock_page}
    )
    fixed_timestamp = int(time.time())
    monkeypatch.setattr(time, 'time', lambda: fixed_timestamp)
    requests = []
    async for req_or_item in spider.parse(mock_response):
        if isinstance(req_or_item, Request): requests.append(req_or_item)
    assert len(requests) == 1
    req = requests[0]
    assert req.meta.get("number") == str(fixed_timestamp)
    assert req.meta.get("title") == "Test Item No Number"

# --- Tests for parse_details ---

@pytest.mark.asyncio
@patch('os.makedirs')
@patch('os.path.exists')
@patch('builtins.open', new_callable=mock_open)
async def test_parse_details_with_attachments(mock_file_open_fn, mock_os_exists, mock_os_makedirs):
    spider = GbsaSpider()
    # Ensure output_dir is set for the spider instance
    spider.output_dir = 'output/gbsa' # Default, but good to be explicit
    
    # Mock os.path.exists to simulate directory not existing initially
    mock_os_exists.return_value = False 

    mock_playwright_page = MockPlaywrightPage()
    
    detail_page_url = "https://www.gbsa.or.kr/board/notice.do?bno=12345"
    
    mock_html_content = """
    <html><body>
        <div id="content"><h1>Detail Title</h1><p>This is the main content.</p></div>
        <table class="bbs-view"><tbody><tr><td>Attachments</td><td>
            <ul>
                <li><a href="/path/to/file1.pdf">File 1 (PDF)</a></li>
                <li><a href="/path/to/file2.zip">File 2 &lt;ZIP&gt;</a></li>
            </ul>
        </td></tr></tbody></table>
    </body></html>
    """

    meta_info = {
        "playwright_page": mock_playwright_page,
        "number": "test_num_123",
        "title": "Test Detail Title"
    }
    mock_response = HtmlResponse(
        url=detail_page_url,
        body=mock_html_content,
        encoding='utf-8',
        meta=meta_info.copy() # Use a copy to avoid modification by spider if any
    )

    requests = []
    # parse_details is an async generator
    async for req_or_item in spider.parse_details(mock_response):
        if isinstance(req_or_item, Request):
            requests.append(req_or_item)
        # parse_details should not yield items, only requests for attachments

    expected_attachment_dir = f"{spider.output_dir}/{meta_info['number']}"
    mock_os_exists.assert_called_once_with(expected_attachment_dir)
    mock_os_makedirs.assert_called_once_with(expected_attachment_dir)

    expected_md_filename = f"{spider.output_dir}/{meta_info['number']}.md"
    mock_file_open_fn.assert_called_once_with(expected_md_filename, 'w', encoding='utf-8')
    
    # Prepare expected markdown content based on spider's logic
    title_from_meta = meta_info['title']
    # Simulate main_content_html extraction and cleaning as in spider
    main_content_html = """<h1>Detail Title</h1><p>This is the main content.</p>""" # From mock_html_content and selector
    cleaned_content = re.sub(r'<[^>]+>', ' ', main_content_html).strip()
    cleaned_content = re.sub(r'\s+', ' ', cleaned_content).strip() # Spider uses this too
    
    expected_written_md = f"# {title_from_meta}\n            {cleaned_content}\n            "
    
    mock_file_handle = mock_file_open_fn()
    # Check the content written to the file
    # Ensure this matches exactly, including newlines and spacing from f-string
    mock_file_handle.write.assert_called_once_with(expected_written_md)

    assert len(requests) == 2, "Expected 2 attachment requests"
    attachment_link_texts = ["File 1 (PDF)", "File 2 <ZIP>"] # Text content of <a> tags

    for i, req in enumerate(requests):
        assert req.callback == spider.save_attachment
        assert req.meta["playwright"] is True
        assert req.meta["playwright_include_page"] is True # Ensure this is set for save_attachment
        assert req.meta["attachment_dir"] == expected_attachment_dir
        
        expected_cleaned_filename = clean_filename(attachment_link_texts[i])
        assert req.meta["filename"] == expected_cleaned_filename
        assert req.meta["errback"] == spider.errback
        assert req.dont_filter is True
        
        # Attachment request URL construction in spider:
        # current_url = response.url (detail_page_url)
        # attachment_url = f"{current_url}&carrot={index}"
        assert req.url == f"{detail_page_url}&carrot={i+1}" 

        assert "playwright_page_methods" in req.meta
        assert len(req.meta["playwright_page_methods"]) == 1
        page_method = req.meta["playwright_page_methods"][0]
        
        assert page_method.method == click_and_handle_download # Direct function reference
        
        expected_click_selector = f":nth-match({spider.attachment_links_selector}, {i+1})"
        # click_and_handle_download args are passed as kwargs in PageMethod
        assert page_method.kwargs["selector"] == expected_click_selector
        assert page_method.kwargs["save_path"] == expected_attachment_dir
        assert page_method.kwargs["file_name"] == expected_cleaned_filename

    assert mock_playwright_page.is_closed(), "Playwright page was not closed after parse_details"

@pytest.mark.asyncio
@patch('os.makedirs')
@patch('os.path.exists')
@patch('builtins.open', new_callable=mock_open)
async def test_parse_details_no_attachments(mock_file_open_fn, mock_os_exists, mock_os_makedirs):
    spider = GbsaSpider()
    spider.output_dir = 'output/gbsa_no_attach' # Use a different dir for clarity if needed

    # Simulate directory already existing
    mock_os_exists.return_value = True

    mock_playwright_page = MockPlaywrightPage()
    detail_page_url = "https://www.gbsa.or.kr/board/notice.do?bno=56789"
    
    mock_html_content_no_attachments = """
    <html><body>
        <div id="content"><h1>Detail Title No Attach</h1><p>Main content without attachments.</p></div>
        <table class="bbs-view"><tbody><tr><td>No attachments here</td><td>
            <ul></ul> <!-- Empty list -->
        </td></tr></tbody></table>
    </body></html>
    """
    meta_info = {
        "playwright_page": mock_playwright_page,
        "number": "test_num_456",
        "title": "Test Detail No Attachments"
    }
    mock_response = HtmlResponse(
        url=detail_page_url,
        body=mock_html_content_no_attachments,
        encoding='utf-8',
        meta=meta_info.copy()
    )

    requests = []
    async for req_or_item in spider.parse_details(mock_response):
        if isinstance(req_or_item, Request):
            requests.append(req_or_item)

    assert len(requests) == 0, "Expected no attachment requests when none are present"

    expected_attachment_dir = f"{spider.output_dir}/{meta_info['number']}"
    mock_os_exists.assert_called_once_with(expected_attachment_dir)
    # os.makedirs should NOT be called if os.path.exists returns True
    mock_os_makedirs.assert_not_called()

    expected_md_filename = f"{spider.output_dir}/{meta_info['number']}.md"
    mock_file_open_fn.assert_called_once_with(expected_md_filename, 'w', encoding='utf-8')
    
    title_from_meta = meta_info['title']
    main_content_html = """<h1>Detail Title No Attach</h1><p>Main content without attachments.</p>"""
    cleaned_content = re.sub(r'<[^>]+>', ' ', main_content_html).strip()
    cleaned_content = re.sub(r'\s+', ' ', cleaned_content).strip()
    expected_written_md = f"# {title_from_meta}\n            {cleaned_content}\n            "
    mock_file_handle = mock_file_open_fn()
    mock_file_handle.write.assert_called_once_with(expected_written_md)

    assert mock_playwright_page.is_closed(), "Playwright page was not closed"
```
