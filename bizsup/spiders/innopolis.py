# -*- coding: utf-8 -*-
from bizsup.utils import abort_request, create_output_directory
from bizsup.spiders.base import BaseSpider

class InnopolisSpider(BaseSpider):
    name = "innopolis"
    allowed_domains = ['innopolis.or.kr']
    start_urls = ['https://www.innopolis.or.kr/newBusiness?menuId=MENU01028']
    base_url = 'https://www.innopolis.or.kr'
    output_dir = 'output/innopolis'
    # base.py 상속받음.
    # page_count = 0
    # max_pages = 3
    # div#business-city1-1 ul li a
    items_selector = "div#business-city1-1 ul li  div div strong.title"
    # item_title_selector = "div#business-city1-1 ul li div div strong.title::text"
    # click_selector = "div#business-city1-1 ul li a"
    details_page_main_content_selector = "article.board-view"
    attachment_links_selector = "div.download-list ul li a"
    next_page_url = "https://www.innopolis.or.kr/newBusiness?menuId=MENU01028&gubun=0&categoryId=&pageNum={next_page}&schType=1&schText="

    custom_settings = {
        "PLAYWRIGHT_ABORT_REQUEST": abort_request,
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        create_output_directory(self.output_dir)