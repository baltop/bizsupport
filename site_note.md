
전체 :   첨부파일 중에서  png jpg 같은 이미지 파일은 다운로드 하지 않음. 실제로는 설정에서 이미지파일 건너뛰기가 되어 있음. html페이지에 수많은 이미지 파일을 다 받을 수 없어서 건너뛰기로 설정함.

파일 다운로드에서 jpg png이면 바로    리턴하도록 ㅅ소스 수정할 것. 그부분 로그 남기는 부분도 print대신 loger로 수정해 야 함.

buci        bucheoncci   타이틀 제목만 가져옴. 목록 리스트에서 클릭을 하면 응당코드는 200이지만 내용은 잘못된 주소라는 에러 페이지가 리턴됨. 아마도 자바스크립트에 값이 제대로 submit 되지 않는 걸로 보임.

ccei            selector를 못찾음.  ccei 전체가 한 사이트를 공유. 전체로 가져오면 되는 곳. 스크립트로 다이나믹 사이트. vue react.
cceichungbuk   -  아마도 페이지 로드 후에 특정 element  를 다시 로드 하는 듯. 시작시 item_selector를 찾지 못함. 충북창조경제혁신센터인데 실제 홈페이지는 통합으로 되어 있어서 통합에서 전체를 다운받으면 각 지점의 것을 별도로 받을 필요 없어 보임. 파일다운로드 안됨.
cceiJeonnam       잘됨. 여기는 파일 다운로드 되네. 위에랑 비교해봐야 할 듯.

cbtp      base.py 상속 받는 방식으로 수정. 잘됨.  페이지네이션에 문제 있음.  offset값이 뭔지 확인해봐야함.
cnsp     -    ok
cnspcom            ok cnspcom과 같은 곳. 중복.
dgtp          에러. 디테일페이지 로드 안됨.
dicia   -  한번에 작동
gbsa               ok 중복제목이 있어서 중간에 중단됨. 똑같은 제목으로 여러번 올림. 중복제목은 수정했음.
gbtp       에러.
gcon            1ok
geri            base.py 상속  잘됨    똑같은 제목으로 여러번 올림.
gica            ok    똑같은 제목으로 여러번 올림.
innopolis       base.py 상속  잘됨.      파일 다운로드에 시간초과 에러 발생. 실제로 사이트에 가서 다운로드해도 오래 걸림.
itp             예전방식. 수정안함.   page 안에서 직접 playwright를 사용하는 샘플. 실제 작동은 안함.
jejutp        잘됨.    다음 페이지 넘어가기가 안됨.  1페이지만 처리.
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
          


https://hamancci.korcham.net/front/board/boardContentsListPage.do?boardId=10521&menuId=10057

hamancci        상공회의소 계열 함안 상공회의소.    ajax로 페이지 가져오는데  scrapy-playwright에서 
    raise rewrite_error(error, f"{parsed_st['apiName']}: {error}") from None
playwright._impl._errors.TimeoutError: Page.wait_for_selector: Timeout 180000ms exceeded.
Call log:
  - waiting for locator("div#contentsarea") to be visible

에러 발생함.





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





