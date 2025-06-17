# -*- coding: utf-8 -*-
from bizsup.utils import abort_request, create_output_directory
from bizsup.spiders.base import BaseSpider

class KisaSpider(BaseSpider):
    name = "kisa"
    allowed_domains = ['kisa.or.kr']
    start_urls = ['https://www.kisa.or.kr/401']
    base_url = 'https://www.kisa.or.kr'
    output_dir = 'output/kisa'
    # base.py 에서 상속함.
    # page_count = 0
    # max_pages = 2
    items_selector = "table.notice tbody tr  td.sbj a"
    # item_title_selector = " td.sbj a::text"
    # click_selector = "table.notice tbody tr td.sbj a"
    details_page_main_content_selector = "section.lb_con"
    attachment_links_selector = "ul li.file a[href='#fnPostAttachDownload']"
    next_page_url = "https://www.kisa.or.kr/401?page={next_page}&searchDiv=10&searchWord="

    custom_settings = {
        "PLAYWRIGHT_ABORT_REQUEST": abort_request,
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        create_output_directory(self.output_dir)