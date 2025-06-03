# KITECH 웹사이트 분석 결과

## URL
https://www.kitech.re.kr/research/page1-1.php

## 페이지 분석
- **페이지 제목**: 사업공고 목록 - 알림마당 - 한국생산기술연구원
- **인코딩**: EUC-KR
- **페이지 타입**: 정적 HTML 목록 페이지

## HTML 구조 분석

### 메인 목록 테이블
- **테이블 클래스**: `table_board`
- **테이블 구조**: 
  ```html
  <table class="table_board">
    <caption>사업공고 목록 : 제목, 첨부파일, 등록일로 구성되어 있습니다.</caption>
    <thead>
      <tr>
        <th style="width:60px">번호</th>
        <th>제목</th>
        <th style="width:100px" class="td_hide">첨부파일</th>
        <th style="width:100px" class="td_hide">등록일</th>
      </tr>
    </thead>
    <tbody>
      <!-- 목록 항목들 -->
    </tbody>
  </table>
  ```

### 목록 항목 구조
각 목록 항목은 `<tr>` 태그로 구성되며, 다음과 같은 구조를 가집니다:

```html
<tr class="center">
  <td>639</td>  <!-- 번호 -->
  <td class="left">
    <div -class="dotdotdot">
      <a rel="noopener noreferrer" href="javascript:goDetail(680)" class="orange" title="제목">
        제목 텍스트
      </a>
    </div>
    <div class="td_show">
      첨부파일: <a href="다운로드링크">...</a>
      등록일: 2025-05-19
    </div>
  </td>
  <td class="td_hide">첨부파일 링크</td>
  <td class="td_hide">2025-05-19</td>
</tr>
```

## CSS 선택자 분석

### 1. 목록 테이블 선택자
- **테이블**: `table.table_board`
- **테이블 본문**: `table.table_board tbody`
- **목록 행**: `table.table_board tbody tr`

### 2. 상세 링크 선택자
- **링크 요소**: `table.table_board tbody tr td.left div a[href*="goDetail"]`
- **링크 텍스트**: `table.table_board tbody tr td.left div a[href*="goDetail"]` (텍스트 내용)
- **링크 제목**: `table.table_board tbody tr td.left div a[href*="goDetail"]` (title 속성)

### 3. 기타 정보 선택자
- **번호**: `table.table_board tbody tr td:first-child`
- **등록일**: `table.table_board tbody tr td:last-child`
- **첨부파일**: `table.table_board tbody tr td:nth-child(3) a`

## JavaScript 동작 분석

### goDetail() 함수
```javascript
function goDetail(idx){
  var param = {
    idx: idx
  }
  var url = "page1-2.php";
  postGoDetail(param, url);
}
```

- **상세 페이지 URL**: `page1-2.php`
- **파라미터**: `idx` (각 공고의 고유 ID)
- **전송 방식**: POST 방식으로 폼 데이터 전송

## Scrapy-Playwright용 선택자 추천

### 목록 페이지
```python
# 목록 테이블
list_table = 'table.table_board'

# 목록 항목들
list_items = 'table.table_board tbody tr'

# 상세 링크 (클릭용)
detail_links = 'table.table_board tbody tr td.left div a[href*="goDetail"]'

# 제목 텍스트
title_text = 'table.table_board tbody tr td.left div a[href*="goDetail"]::text'

# 등록일
date_text = 'table.table_board tbody tr td:last-child::text'
```

### JavaScript 링크 처리
이 사이트는 `javascript:goDetail(idx)` 형태의 JavaScript 링크를 사용하므로:
1. Scrapy-Playwright의 `page.click()` 메서드 사용 필요
2. 각 링크를 클릭하여 상세 페이지로 이동
3. POST 요청을 통해 `page1-2.php`로 데이터 전송

## 권장 스크래핑 전략
1. 목록 페이지에서 모든 `goDetail` 링크 추출
2. 각 링크를 순차적으로 클릭하여 상세 페이지 방문
3. 상세 페이지에서 내용 및 첨부파일 정보 추출
4. 브라우저 백 버튼으로 목록 페이지로 돌아가서 다음 항목 처리