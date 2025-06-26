# -*- coding: utf-8 -*-
from bizsup.utils import abort_request, create_output_directory
from bizsup.spiders.base import BaseSpider

class TtpSpider(BaseSpider):
    name = "ttp"
    allowed_domains = ['technopark.kr']
    start_urls = ['http://www.technopark.kr/businessboard']
    base_url = 'http://www.technopark.kr'
    output_dir = 'output/ttp'
    
    # 실제 HTML 구조에 맞게 수정
    items_selector = "tbody tr td.tit a"
    
    details_page_main_content_selector = "div.xe_content, div.board_add_file"
    attachment_links_selector = "div.board_add_file ul li a"
    
    # conf/ttp.json에서 가져온 페이지네이션 패턴
    next_page_url = "http://www.technopark.kr/index.php?mid=businessboard&page={next_page}"

    custom_settings = {
        "PLAYWRIGHT_ABORT_REQUEST": abort_request,
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        create_output_directory(self.output_dir)