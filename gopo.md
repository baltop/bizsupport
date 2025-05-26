레코드에서 읽어온 field를 아래 대입한다.

start_URL : {start_URL}

- start_URL은 목록-상세로 이루어진 페이지네이션 게시판 구조의 첫페이지이다.

- 목록 페이지에는 items가 10개에서 20개 정도 나열되어 있다.

- 목록 페이지에는 상세 페이지로 이동할 수 있는 링크가 있다.

- rplan 이라는 디렉토리를 만들고 그 아래에 {site_code} 디렉토리를 만들고 거기에 모든 산출물을 저장한다.

- start_URL 을 curl로 fetch하여 {site_code}_list.html로 저장한다.

- {site_code}_list.html을 분석하여 item 상세 페이지에서 접근할 수 있는 links를 추출한다. 

- link는 javascript link일 수 있고 href의 url link일 수 있다.

- url link 타입인 경우, 추후 개발자가 사용할 수 있도록 link를 뽑아 낼수 있는 css selector를 추출하여 저장한다.

- css selector는 반드시 html 문서상에 있는 것인지 확인하고 저장한다. grep 으로 해당 문서에서 검색 확인해야 한다.

- javascript link인 경우, onclick의 javascript call 하는 부분을 저장한다. javascript의 이름으로 function body를 html에서 추출하여 저장한다. html 문서상에 없는 경우 include 된 js 파일을 fetch하여 찾는다. 

- javascript는 call하는 부분과 function body자체 부분 2가지를 저장한다.

- class 명으로 selector를 구하는 경우 임의로 추측하지 말고 반드시 HTML 문서상에 있는 것으로 확인하고 사용한다.

- selector를 확정했다면 html상에서 실제로 그 selector로 접근하여 url link를 추출할 수 있는지 확인한다.

-결과를 아래와 같은 형식으로 markdown 파일을 생성하고 저장한다. 파일명은 {site_code}_link.md로 한다.


```
list link
- javascript yes/no : 
- selector : css selector
- link pattern : url 
- link example : http://www.naver.com

- javascript function body:
- javascript call part:

```



