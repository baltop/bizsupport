# -*- coding: utf-8 -*-
from bizsup.utils import abort_request, create_output_directory
from bizsup.spiders.base import BaseSpider

class GbtpSpider(BaseSpider):
    name = "gbtp"
    allowed_domains = ['gbtp.or.kr']
    start_urls = ['https://www.gbtp.or.kr/user/board.do?bbsId=BBSMSTR_000000000021']
    base_url = 'https://www.gbtp.or.kr'
    output_dir = 'output/gbtp'
    
    # 실제 HTML 구조에 맞게 수정 - 공고명이 두 번째 셀에 있음
    items_selector = "table tbody tr td:nth-child(2) a"
    
    details_page_main_content_selector = "table tbody tr td"
    attachment_links_selector = "table tbody tr td a[href*='javascript:;']"
    
    # conf/gbtp.json에서 가져온 페이지네이션 패턴
    next_page_url = "https://www.gbtp.or.kr/user/board.do?bbsId=BBSMSTR_000000000021&pageIndex={next_page}"

    custom_settings = {
        "PLAYWRIGHT_ABORT_REQUEST": abort_request,
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        create_output_directory(self.output_dir)