# -*- coding: utf-8 -*-
from bizsup.utils import abort_request, create_output_directory
from bizsup.spiders.base import BaseSpider

class GeriSpider(BaseSpider):
    name = "geri"
    allowed_domains = ['geri.re.kr']
    start_urls = ['https://geri.re.kr/html/board_list.asp?board_id=business']
    base_url = 'https://geri.re.kr'
    output_dir = 'output/geri'
    page_count = 0
    max_pages = 2
    items_selector = "div.notice_box ul li"
    item_title_selector = "a span.t2 span.txt::text"
    click_selector = "div.notice_box ul li a"
    details_page_main_content_selector = "div.notice_view"
    attachment_links_selector = "dl dd a"
    next_page_url = "https://geri.re.kr/html/board_list.asp?search_name=&search_str=&board_id=business&page={next_page}"

    custom_settings = {
        "PLAYWRIGHT_ABORT_REQUEST": abort_request,
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        create_output_directory(self.output_dir)