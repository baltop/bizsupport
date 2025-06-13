buci        bucheoncci   타이틀 제목만 가져옴. 목록 리스트에서 클릭을 하면 응당코드는 200이지만 내용은 잘못된 주소라는 에러 페이지가 리턴됨. 아마도 자바스크립트에 값이 제대로 submit 되지 않는 걸로 보임.

ccei            selector를 못찾음.  ccei 전체가 한 사이트를 공유. 전체로 가져오면 되는 곳. 스크립트로 다이나믹 사이트. vue react.
cceichungbuk.py   -  아마도 페이지 로드 후에 특정 element  를 다시 로드 하는 듯. 시작시 item_selector를 찾지 못함. 충북창조경제혁신센터인데 실제 홈페이지는 통합으로 되어 있어서 통합에서 전체를 다운받으면 각 지점의 것을 별도로 받을 필요 없어 보임. 파일다운로드 안됨.
cceiJeonnam       잘됨. 여기는 파일 다운로드 되네. 위에랑 비교해봐야 할 듯.

cbtp.py      base.py 상속 받는 방식으로 수정. 잘됨.
cnsp     -    ok
cnspcom            ok
dgtp          에러. 디테일페이지 로드 안됨.
dicia   -  한번에 작동
gbsa               ok
gbtp.py       에러.
gcon            1ok
geri            base.py 상속  잘됨
gica            ok
innopolis       base.py 상속  잘됨.
itp             예전방식. 수정안함.   page 안에서 직접 playwright를 사용하는 샘플. 실제 작동은 안함.
jejutp.py        잘됨.
kidp   -   목록페이지에서 목록 클릭시 상세 페이지로 이동하지 않음.
kidpinline    목록페이지에서 목록 클릭시 상세 페이지로 이동하지 않음.

kisa            1ok
kofpi            상세페이지 로드 안됨.
ltp             잘됨.   실제로는 btp 사이트 
mof             잘됨.    a 아래 span 이 있거나 없거나 함. 그래서 getall() 하고 나중에 join 하는 걸로 수정.
mpt             잘됨   실제로는 itp
mss6   -  한번에 작동
semas           에러  안됨 자바스크립트 다이나믹. vue 나 react
seoultp.py   -   javascript 인경우 파라미터에서 doc id를 꺼내서 이미 알고 있는 url에 파라미터로 대입하여 디테일 페이지로 이동. 독자실행잘됨. BaseSpider 상속 방식으로 수정해서 테스트해볼 필요 있음.

sjtp               잘됨.
snipBottom.py    -     form data 이용해서 post 로 리퀘스트 보내는 샘플.  첫번째 디테일 페이지도 post 이고 다음 pagination도 post 방식으로 하고 있음.
          





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





