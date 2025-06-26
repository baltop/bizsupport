# -*- coding: utf-8 -*-
from bizsup.utils import abort_request, create_output_directory
from bizsup.spiders.base import BaseSpider

class PmsSpider(BaseSpider):
    name = "pms"
    allowed_domains = ['pms.gtp.or.kr']
    start_urls = ['https://pms.gtp.or.kr/web/business/webBusinessList.do']
    base_url = 'https://pms.gtp.or.kr'
    output_dir = 'output/pms'
    
    # 실제 HTML 구조에 맞게 수정 - 공고 제목이 두 번째 셀에 있음
    items_selector = "table tbody tr td:nth-child(2) a"
    
    # 상세 페이지의 정의 목록(dl)과 본문 내용(generic) 포함
    details_page_main_content_selector = "dl, dd, generic, h3, p, img"
    
    # 첨부파일은 definition 안의 download.do 링크들
    attachment_links_selector = "dd a[href*='/common/download.do']"
    
    # conf/pms.json의 page_url이 잘못되어 있음 - 실제 사이트 구조에 맞게 수정
    next_page_url = "https://pms.gtp.or.kr/web/business/webBusinessList.do?pageIndex={next_page}"

    custom_settings = {
        "PLAYWRIGHT_ABORT_REQUEST": abort_request,
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        create_output_directory(self.output_dir)