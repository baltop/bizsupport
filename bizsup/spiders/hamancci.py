# -*- coding: utf-8 -*-
from bizsup.utils import abort_request, create_output_directory
from bizsup.spiders.base import BaseSpider

class HamancciSpider(BaseSpider):
    name = "hamancci"
    allowed_domains = ['korcham.net']
    start_urls = ['https://hamancci.korcham.net/front/board/boardContentsListPage.do?boardId=10521&menuId=10057']
    base_url = 'https://hamancci.korcham.net'
    output_dir = 'output/hamancci'
    # base.py 에서 상속 받음.
    # page_count = 0
    # max_pages = 2
    items_selector = "div.boardlist table tbody tr td.c_title a"

    details_page_main_content_selector = "div#contentsarea"
    attachment_links_selector = "ul.file_view li a"
    next_page_url = "https://hamancci.korcham.net/front/board/boardContentsListPage.do?boardId=10521&menuId=10057&miv_pageNo={next_page}"

    custom_settings = {
        "PLAYWRIGHT_ABORT_REQUEST": abort_request,
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        create_output_directory(self.output_dir)

