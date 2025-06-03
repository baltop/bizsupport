# -*- coding: utf-8 -*-
from bizsup.utils import abort_request, create_output_directory
from .base import BaseSpider

class GbsaSpider(BaseSpider):
    name = "gbsa"
    allowed_domains = ['gbsa.or.kr']
    start_urls = ['https://www.gbsa.or.kr/board/notice.do']
    base_url = 'https://gbsa.or.kr'
    output_dir = 'output/gbsa'
    page_count = 0
    max_pages = 2
    items_selector = "table.bbs-list tbody tr"
    item_title_selector = "td.align_left a::text"
    click_selector = "td.align_left a"
    details_page_main_content_selector = "div#content"
    attachment_links_selector = "table.bbs-view tbody tr td ul li a"
    next_page_url = "https://www.gbsa.or.kr/board/notice.do?pageIndex={next_page}&searchCnd=0&searchWrd=&ozcsrf="

    custom_settings = {
        "PLAYWRIGHT_ABORT_REQUEST": abort_request,
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        create_output_directory(self.output_dir)

