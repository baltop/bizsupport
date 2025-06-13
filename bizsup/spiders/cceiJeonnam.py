# -*- coding: utf-8 -*-
from bizsup.utils import abort_request, create_output_directory
from bizsup.spiders.base import BaseSpider

class CceiJeonnamSpider(BaseSpider):
    name = "cceiJeonnam"
    allowed_domains = ['ccei.creativekorea.or.kr']
    start_urls = ['https://ccei.creativekorea.or.kr/jeonnam/custom/notice_list.do?']
    base_url = 'https://ccei.creativekorea.or.kr'
    output_dir = 'output/cceiJeonnam'
    page_count = 0
    max_pages = 2
    items_selector = "table.tbl1 tbody tr td:nth-child(3) a.tb_title"
    # item_title_selector = "td:nth-child(3) a.tb_title::text"
    # click_selector = "table.tbl1 tbody tr td:nth-child(3) a.tb_title"
    details_page_main_content_selector = "div.contentswrapper"
    attachment_links_selector = "div.vw_download a"
    next_page_url = "https://ccei.creativekorea.or.kr/jeonnam/custom/notice_list.do?&page={next_page}"

    custom_settings = {
        "PLAYWRIGHT_ABORT_REQUEST": abort_request,
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        create_output_directory(self.output_dir)
