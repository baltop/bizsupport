start_URL : https://www.gbtp.or.kr/user/board.do?bbsId=BBSMSTR_000000000021

- start_URL 에 접근해서 html DOM 분석하여 url link를 추출할 수 있는 css selector를 찾거나 javascript link를 분석하여 실제 URL을 추출할 수 있는 방법을 찾아야 한다. playwright mcp 를 이용하여 fetch 하거나 curl를 이용하여 fetch 한다. 또는 scrapy shell을 이용하여 fetch 한다.
- 만약 javascript link로 되어 있다면 그 javascript함수의 body를 분석하여 실제 URL을 추출할 수 있는 방법을 찾아야 한다. 핑요하면  playwright mcp를 이용하여 fetch 한다.
- class 명으로 selector를 구하는 경우 임의로 추측하지 말고 반드시 HTML 문서상에 있는 것으로 확인하고 사용한다.
- selector를 확정했다면 html상에서 실제로 그 selector로 접근하여 url link를 추출할 수 있는지 확인한다.



1. start_URL은 목록 페이지 인데 거기에 나오는 목록들을 접근할 수 있는 Link를 추출해야 하고자 하는데 만약 소스기 URL로 링크되어 있다면 그 링크를 추출할 수 있는 CSS selector를 찾아야 한다. 만약 Link가 javascript로 되어 있다면 그 javascript를 분석하여 실제 URL을 추출할 수 있는 방법을 찾아야 한다. 이것을 list link라 한다.

2. 목록하단에는 페이지네이션 bar가 있는데 이곳에서 다음 페이지로 이동할 수 있는 방법을 찾아야 한다. 만약 페이지네이션 bar가 URL로 되어 있다면 그 URL을 추출할 수 있는 CSS selector를 찾아야 하고 만약 javascript로 되어 있다면 그 javascript를 분석하여 실제 URL을 추출할 수 있는 방법을 찾아야 한다. 이것을 pagination link라 한다.

3. 1번에서 찾은 목록 링크 중에 하나에 navigate를 하면 상세 페이지로 이동하게 되는데 이곳에서 공고의 개요를 추출할 수 있는 CSS selector를 찾아야 한다. 이것을 detail link라 한다.

4. 상세 페이지에서 첨부파일이 있는 경우 그 파일을 다운로드 할 수 있는 링크를 추출할 수 있는 CSS selector를 찾아야 한다. 이것을 attachment link라 한다. 첨부파일이 다운로드 링크가 URL로 되어 있다면 그 URL을 추출할 수 있는 CSS selector를 찾아야 하고 만약 javascript로 되어 있다면 그 javascript를 분석하여 실제 URL을 추출할 수 있는 방법을 찾아야 한다. 이것을 attachment link라 한다.

위의 link들을 전부 추출하고 실재로 접근해서 유효한지도 확인한 후에 다음의 형식으로 markdown 파일을 생성하고 저장한다. 파일명은 gbtp_link.md로 한다. javascript link 인 경우는 javascript yes/no : 항목에 yes를 표시하고 selector 항목은 기입하지 않는다.
javascrip link는 playwright mcp를 이용하여 클릭을 해서 타겟페이지로 이동한 후에 그 페이지의 url을 패턴으로 추출한다. 

javascript 는 함수 body를 찾아서 url을 추출한다.



```
list link
- javascript yes/no : 
- selector : css selector
- link pattern : url 

pagination link
- javascript yes/no :
- selector : css selector
- link pattern : url

detail link
- selector : css selector

attachment link
- javascript yes/no :
- selector : css selector
- link pattern : url
```



