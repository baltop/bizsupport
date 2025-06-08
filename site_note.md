buci        bucheoncci   타이틀 제목만 가져옴. 목록 리스트에서 클릭을 하면 응당코드는 200이지만 내용은 잘못된 주소라는 에러 페이지가 리턴됨. 아마도 자바스크립트에 값이 제대로 submit 되지 않는 걸로 보임.
mss6   -  한번에 작동
cceichungbuk.py   -  아마도 페이지 로드 후에 특정 element  를 다시 로드 하는 듯. 시작시 item_selector를 찾지 못함. 충북창조경제혁신센터인데 실제 홈페이지는 통합으로 되어 있어서 통합에서 전체를 다운받으면 각 지점의 것을 별도로 받을 필요 없어 보임.
kidp   -   목록페이지에서 목록 클릭시 상세 페이지로 이동하지 않음.
dicia   -  한번에 작동
cnsp     -    ok
seoultp.py   -   javascript 인경우 파라미터에서 doc id를 꺼내서 이미 알고 있는 url에 파라미터로 대입하여 디테일 페이지로 이동.
snipBottom.py    -     form data 이용해서 post 로 리퀘스트 보내는 샘플.  첫번째 디테일 페이지도 post 이고 다음 pagination도 post 방식으로 하고 있음.
itp.py               page 안에서 직접 playwright를 사용하는 샘플. 실제 작동은 안함.
jejutp.py     vue 로 만들어진 dynimic page. 에러 해결 안됨.
cbtp.py      base.py 상속 받는 방식으로 수정. 잘됨.
gdtp.py       file download가 안됨. 만들어진 items 의 txt 내용도 엉망임. base상속 방식이 아닌 자체 처리로 변경. 파일 다운로드를 자바스크립트 파싱으로 변경.
innopolis       base.py 상속  잘됨.
geri            base.py 상속  잘됨.
cceiJeonnam       ccei는 안됨. vue 나 react인듯.
kisa            1ok
semas           안됨 자바스크립트 다이나믹. vue 나 react
gcon            1ok
ccei            selector를 못찾음.  ccei 전체가 한 사이트를 공유. 전체로 가져오면 되는 곳. 스크립트로 다이나믹 사이트. vue react.



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





