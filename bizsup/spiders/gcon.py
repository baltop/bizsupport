# -*- coding: utf-8 -*-
from bizsup.utils import abort_request, create_output_directory
from bizsup.spiders.base import BaseSpider

class GconSpider(BaseSpider):
    name = "gcon"
    allowed_domains = ['gcon.or.kr']
    start_urls = ['https://www.gcon.or.kr/gcon/business/gconNotice/list.do?menuNo=200061']
    base_url = 'https://www.gcon.or.kr'
    output_dir = 'output/gcon'
    page_count = 0
    max_pages = 2
    items_selector = "table tbody tr td.title a"
    # item_title_selector = "td.title a::text"
    # click_selector = "td.title a"
    details_page_main_content_selector = "div#content"
    attachment_links_selector = "div.file-list__set__item a"
    next_page_url = "https://www.gcon.or.kr/gcon/business/gconNotice/list.do?menuNo=200061&pageIndex={next_page}"

    custom_settings = {
        "PLAYWRIGHT_ABORT_REQUEST": abort_request,
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        create_output_directory(self.output_dir)
