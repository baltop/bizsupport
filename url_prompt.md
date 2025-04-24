
** 개요 

server_full.cvs 파일을 읽어서 레코드 별로 하나의 scrapy spider코드를 작성해야 한다.
각 레코드는 사이트코드,기관명,start_URL,API_yn으로 데이터가 구성되어 있다.
사이트코드로 spider의 name을 정하고 file명도 {사이트코드}.py로 한다.
domain은 start_URL에서 추출해서 만든다.

각 스파이더의 궁극적인  목적은 start_url에서 가져온 html파일을 파싱하여 공고 목록을 판별하고 공고의 상세페이지를 방문하여 공고내용을 markdown파일로 저장하고 첨부파일이 있는 경우  첨부파일을 다운로드 하여 저장하는데 있다.


** plan 

- start_URL 에 접근해서 html DOM 분석하여 url link를 추출할 수 있는 css selector를 찾거나 javascript link를 분석하여 실제 URL을 추출할 수 있는 방법을 찾아야 한다. playwright mcp 를 이용하여 fetch 하거나 curl를 이용하여 fetch 한다. 또는 scrapy shell을 이용하여 fetch 한다.

- 만약 javascript link로 되어 있다면 그 javascript함수의 body를 분석하여 실제 URL을 추출할 수 있는 방법을 찾아야 한다. 핑요하면  playwright mcp를 이용하여 fetch 한다.

- class 명으로 selector를 구하는 경우 임의로 추측하지 말고 반드시 HTML 문서상에 있는 것으로 확인하고 사용한다.

- selector를 확정했다면 html상에서 실제로 그 selector로 접근하여 url link를 추출할 수 있는지 확인한다.



1. start_URL은 목록 페이지 인데 거기에 나오는 목록들을 접근할 수 있는 Link를 추출해야 하고자 하는데 만약 소스기 URL로 링크되어 있다면 그 링크를 추출할 수 있는 CSS selector를 찾아야 한다. 만약 Link가 javascript로 되어 있다면 그 javascript를 분석하여 실제 URL을 추출할 수 있는 방법을 찾아야 한다. 이것을 list link라 한다.

2. 목록하단에는 페이지네이션 bar가 있는데 이곳에서 다음 페이지로 이동할 수 있는 방법을 찾아야 한다. 만약 페이지네이션 bar가 URL로 되어 있다면 그 URL을 추출할 수 있는 CSS selector를 찾아야 하고 만약 javascript로 되어 있다면 그 javascript를 분석하여 실제 URL을 추출할 수 있는 방법을 찾아야 한다. 이것을 pagination link라 한다.

3. 1번에서 찾은 목록 링크 중에 하나에 navigate를 하면 상세 페이지로 이동하게 되는데 이곳에서 공고의 개요를 추출할 수 있는 CSS selector를 찾아야 한다. 이것을 detail link라 한다.

4. 상세 페이지에서 첨부파일이 있는 경우 그 파일을 다운로드 할 수 있는 링크를 추출할 수 있는 CSS selector를 찾아야 한다. 이것을 attachment link라 한다. 첨부파일이 다운로드 링크가 URL로 되어 있다면 그 URL을 추출할 수 있는 CSS selector를 찾아야 하고 만약 javascript로 되어 있다면 그 javascript를 분석하여 실제 URL을 추출할 수 있는 방법을 찾아야 한다. 이것을 attachment link라 한다.



** 단계별 상세 처리 방안

- scrapy 프레임워크를 이용하여 코딩한다.  스파이더만  코딩한다. 

- 새로 작성하는 snip 스파이더의 소스인 locgov.py 이외에는 수정하거나 변경하지 말것.

- start_url을 fetch mcp server를 이용하여 fetch시  raw=true, max_length=500000 옵션으로 다운 받은 후에 html의 DOM을 구조적으로 parsing해서 item 목록의  url 들을 추출할 selector(element, id, class)를 찾아내야 한다.

- fetch에 실패하면 즉시 프로세스를 중단하고 다음 레코드로 넘어간다. 

- start_URL은 사업 공고의 목록 페이지 이다. 목록 페이지는 대개 10개에서 20개 정도의 item목록을 가지고 있고 대부분은 html의 table 태그로 구성되어 있다. 가끔 html의 ul 태그로 이루어진 경우도 있다.  

- item 목록은 item의 id번호, item의 제목, 작성자, 작성일 등으로 구성되어 있는데 사이트 마다 내용이나 순서는 조금씩 다르다.

- dom element를 parsing 하여  id번호를 찾을 수 있는 selector와 제목에 걸린 링크를 가져올수 있는 selector를 코드에 추가해 줘야 한다.

- item 목록은 대개 제목에 URL 또는 javascript로 링크가 들어있고 상세페이지에 접근할 수 있다. 

- 상세페이지 링크가 URL로 되어 있는 사이트는 url로 상세페이지를 가져오도록 코딩하면 되는데, 링크가 javascript로 되어 있는 경우는 scrapy-playwright를 이용하여 click으로 가져오도록 코딩해야 한다.

- item상세 페이지는 공고의 개요가 있는데 그 내용을 {id번호}.md 파일에 저장하고 상세 페이지 상에 첨부파일이 있는 경우  그 파일을 다운로드하여 id번호로 디렉토리를 만들고 거기에 저장하도록 코딩한다.

- 파일 다운로드 링크가 url이면 url을 이용하여 다운로드하고 javascript로 되어 있으면 scrapy-playwright를 이용하여 click하여 다운로드 하도록 코딩한다.

- item 목록상의 item 들을 다 처리한 후에 pagination bar에서 다음 페이지로 이동할 수 있는 방법을 찾아 코딩해야 한다.

- 다음 페이지가 링크 URL로 되어 있는 경우와 javascript로 되어 있는 경우가 있으니 각각에 맞게 코딩해야 한다.

- 사이트의 코드명에 해당하는 spider 를 만든다. ( 예:  사이트코드명.py )

- 페이지가 3페이지가 넘으면 반복을 중단한다.

- `scrapy crawl locgov` 으로 테스트 하여 에러가 발생할 경우에 소스를 수정해줘. 별도의 테스트용 소스코드는 만들지 말 것.

- scrapy shell 명령으로 debug해 볼  것.

** 주의 지항

- 첨부파일 파일명은 Content-Disposition 헤더에 들어 있는 filename을 사용하고 만약 filename이 없으면 Content-Type 헤더로 확장자를 추측하여 파일명을 만들어야 한다. 만약 조건이 맞는 것이 없으면 그냥 파일명을 반환할 것. 뒤에 '.bin' 을 붙이지 말것.

- 첨부 파일 다운로드시에  # 한글 파일명 처리를 해야 할 경우 
  
  ```
  filename = filename.encode('latin1').decode('utf-8', errors='ignore')
  ```
  대신에 
  ```
  filename = unquote(server_filename)
  ```
  을 사용할 것.
  
  