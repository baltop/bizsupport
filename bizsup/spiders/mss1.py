
from bizsup.spiders.base import BaseSpider
from bizsup.utils import abort_request, create_output_directory

class Mss1Spider(BaseSpider):
    name = "mss1"
    allowed_domains = ['mss.go.kr']
    start_urls = ['https://www.mss.go.kr/site/seoul/ex/bbs/List.do?cbIdx=146']
    base_url = 'https://mss.go.kr'
    output_dir = 'output/mss1'

    items_selector = "div.board_list table tbody tr td.subject a"

    details_page_main_content_selector = "div.area1"

    attachment_links_selector = "td.file_list ul li div.link a"
    
    next_page_url = "https://www.mss.go.kr/site/seoul/ex/bbs/List.do?cbIdx=146&pageIndex={next_page}"
    
    custom_settings = {
        "PLAYWRIGHT_ABORT_REQUEST": abort_request,  # Aborting unnecessary requests
    }

    def __init__(self, *args, **kwargs):
        super(Mss1Spider, self).__init__(*args, **kwargs)
        create_output_directory(self.output_dir)  # Create output directory if it doesn't exist

