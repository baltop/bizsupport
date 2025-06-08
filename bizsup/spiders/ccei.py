# -*- coding: utf-8 -*-
from bizsup.utils import abort_request, create_output_directory
from bizsup.spiders.base import BaseSpider

class CceiSpider(BaseSpider):
    name = "ccei"
    allowed_domains = ['ccei.creativekorea.or.kr']
    start_urls = ['https://ccei.creativekorea.or.kr/service/business_list.do']
    base_url = 'https://ccei.creativekorea.or.kr'
    output_dir = 'output/ccei'
    page_count = 0
    max_pages = 2
    items_selector = "table.tb03 tbody tr"
    item_title_selector = "td.tb_title a::text"
    click_selector = "table.tb03 tbody tr td.tb_title a"
    details_page_main_content_selector = "div.brd_area"
    attachment_links_selector = "div.vw_download a"
    next_page_url = "https://ccei.creativekorea.or.kr/service/business_list.do&page={next_page}"

    custom_settings = {
        "PLAYWRIGHT_ABORT_REQUEST": abort_request,
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        create_output_directory(self.output_dir)