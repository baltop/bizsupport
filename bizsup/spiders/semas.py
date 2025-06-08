# -*- coding: utf-8 -*-
from bizsup.utils import abort_request, create_output_directory
from bizsup.spiders.base import BaseSpider

class SemasSpider(BaseSpider):
    name = "semas"
    allowed_domains = ['semas.or.kr']
    start_urls = ['https://www.semas.or.kr/web/board/webBoardList.kmdc?bCd=2001&pNm=BOA0121']
    base_url = 'https://www.semas.or.kr'
    output_dir = 'output/semas'
    page_count = 0
    max_pages = 2
    items_selector = "a.aconbox"
    item_title_selector = "ul li.tit div.cut_text1::text"
    click_selector = "a.aconbox"
    details_page_main_content_selector = "div.u-page.cont-max"
    attachment_links_selector = "div.file-group div button.q-btn.q-btn-item.non-selectable.no-outline.q-btn--standard.q-btn--rectangle"
    next_page_url = "https://www.semas.or.kr/web/board/webBoardList.kmdc?bCd=2001&pNm=BOA0121&page={next_page}"

    custom_settings = {
        "PLAYWRIGHT_ABORT_REQUEST": abort_request,
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        create_output_directory(self.output_dir)