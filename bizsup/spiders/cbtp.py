# -*- coding: utf-8 -*-
from bizsup.utils import abort_request, create_output_directory
from .base import BaseSpider

class CbtpSpider(BaseSpider):
    name = "cbtp"
    allowed_domains = ['cbtp.or.kr']
    start_urls = ['https://www.cbtp.or.kr/index.php?control=bbs&board_id=saup_notice&lm_uid=387']
    base_url = 'https://www.cbtp.or.kr'
    output_dir = 'output/cbtp'
    page_count = 0
    max_pages = 2
    items_selector = "table.bbs_default_list tbody tr"

    item_title_selector = "table.bbs_default_list tbody tr td.subject a::text"
    click_selector = "table.bbs_default_list tbody tr td.subject a"

    details_page_main_content_selector = "div.sub_contents"
    attachment_links_selector = "ul.attach.clearfix li a"
    
    next_page_url = "https://www.cbtp.or.kr/index.php?control=bbs&lm_uid=387&board_id=saup_notice&page={next_page}&offset=16&task=list&list_mode=&search_field=&search_str=&opt_a=&categ=&&categ=&lm_uid=387"
    
    custom_settings = {
        "PLAYWRIGHT_ABORT_REQUEST": abort_request,
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        create_output_directory(self.output_dir)
