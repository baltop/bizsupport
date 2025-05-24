mss6   -  한번에 작동
cceichungbuk.py   -  아마도 페이지 로드 후에 특정 element  를 다시 로드 하는 듯. 시작시 item_selector를 찾지 못함. 충북창조경제혁신센터인데 실제 홈페이지는 통합으로 되어 있어서 통합에서 전체를 다운받으면 각 지점의 것을 별도로 받을 필요 없어 보임.
kidp   -   목록페이지에서 목록 클릭시 상세 페이지로 이동하지 않음.
dicia   -  한번에 작동
cnsp     -    ok
seoultp.py   -   javascript 인경우 파라미터에서 doc id를 꺼내서 이미 알고 있는 url에 파라미터로 대입하여 디테일 페이지로 이동.
snipBottom.py    -     form data 이용해서 post 로 리퀘스트 보내는 샘플.  첫번째 디테일 페이지도 post 이고 다음 pagination도 post 방식으로 하고 있음.
itp.py               page 안에서 직접 playwright를 사용하는 샘플. 실제 작동은 안함.



-----
href에 그냥 주소가 들어있는 경우 다음과 같이 해도 된다.
            detail_url_attr = item.css("td.subject a::attr(href)").get()
            if detail_url_attr:
                detail_url = urljoin(response.url, detail_url_attr)
-----
또 다른 샘플
            detail_url_elem = title_elem.css("::attr(href)")
            if detail_url_elem:
                # Check if it's a JavaScript function call
                href = detail_url_elem.get()
                if href.startswith("javascript:"):
                    # Extract parameters from JavaScript function
                    js_params = re.search(r'javascript:fnGoView\(\'([^\']+)\'', href)
                    if js_params:
                        bizSeq = js_params.group(1)
                        detail_url = f"https://www.kita.net/asocBiz/asocBiz/asocBizOngoingView.do?bizSeq={bizSeq}"
                        
------
post  샘플
        # This site uses API calls for data, so we'll make a POST request to the API
        formdata = {
            "currentPageNo": "1",
            "recordCountPerPage": "10",
            "section": "business1"
        }
        
        yield scrapy.FormRequest(
            url=self.api_url,
            formdata=formdata,
            callback=self.parse_api,
            meta={"playwright": True, "page": 1}
        )
------





