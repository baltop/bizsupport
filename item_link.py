# -*- coding: utf-8 -*-
import csv
import subprocess
import os
import sys
import time


# 이 스크립트는 사이트 코드와 URL이 포함된 CSV 파일을 읽고, Claude Code에 최적화된 명령어를 생성하여 실행합니다.
# 이 명령어는 웹 페이지의 CSS selector를 추출하기 위해 설계되었습니다.

def execute_bash_command(command):
    try:
        result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # print("stdout", result.stdout.decode('utf-8'))
        print("stderr", result.stderr.decode('utf-8'))
        return result.stdout.decode('utf-8')
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")
        return None
    


print("Reading CSV file...")
file_path = os.path.join(os.path.dirname(__file__), '0424full.csv')
with open(file_path, mode='r', encoding='utf-8') as file:
    reader = csv.reader(file)
    data = [row for row in reader]
    for index, row in enumerate(data):
        if index <= 60:
            continue
        if index > 81:
            break
        print(row[0], row[2])  # Replace 0 with the index of the desired field (e.g., site_code column index)

        com = (f"~/.claude/local/claude --dangerously-skip-permissions -p '사이트코드: {row[0]}, URL: {row[2]}에 접근하여 웹페이지를 분석하라. "
                "먼저 WebFetch tool을 사용하여 HTML을 가져와서 분석하고, 필요시에만 playwright MCP를 사용하라. "
                "이 URL은 공고/게시물 목록을 보여주는 list page이다. "
                "각 게시물의 링크를 클릭하면 상세 페이지로 이동한다. "
                "다음 작업을 순서대로 수행하라: "
                "1. HTML 구조 분석 "
                "2. CSS selector 추출 (다음 규칙 준수): "
                "   - class/id 기반 selector 사용 (예: table.tbl1, div.content) "
                "   - 속성 selector 금지 (예: table[aria-label], a[href*=notice]) "
                "   - nth-child 사용 금지 "
                "   - 대괄호 포함 selector 금지 "
                "3. 추출할 selector들: "
                "   - items_selector: 게시물 목록의 각 행 "
                "   - item_title_selector: 게시물 제목 텍스트 "
                "   - click_selector: 클릭할 링크 "
                "   - details_page_url: 상세페이지 URL 예시 "
                "   - details_page_main_content_selector: 상세페이지 본문 "
                "   - attachment_links_selector: 첨부파일 링크 "
                "4. 사이트 유형 판단: JavaScript 필요시 scrapy-playwright, 아니면 scrapy만 "
                "5. 결과를 /home/baltop/work/bizsupport/bizsup/items/{row[0]}.txt에 저장 "
                "파일 형식: "
                "items_selector = \"table.bbs-list tbody tr\" "
                "item_title_selector = \"td.title a::text\" "
                "click_selector = \"td.title a\" "
                "details_page_url = \"/board_detail?id=829\" "
                "details_page_main_content_selector = \"div.content\" "
                "attachment_links_selector = \"div.attach a\" "
                "javascript site = need scrapy-playwright or url link site = need scrapy only'")
        

        result = execute_bash_command(com)  # Example command    
        if result:
            print(result)  # Print the output of the command




# cceiChungbuk https://ccei.creativekorea.or.kr/chungbuk/custom/notice_list.do?
# stderr 
# CSS selectors extracted and saved to `/items/cceichungbuk.txt`:

# - **items_selector**: `"table.tbl1 tbody tr"` - Main table rows containing notice items
# - **item_title_selector**: `"table.tbl1 tbody tr td a.tb_title::text"` - Notice title text
# - **click_selector**: `"table.tbl1 tbody tr td a.tb_title"` - Clickable title links (uses JavaScript)
# - **details_page_url**: `"/chungbuk/custom/notice_view.do?no=35358"` - Detail page URL pattern
# - **details_page_main_content_selector**: `"div.brd_viewer"` - Main content area in detail page
# - **attachment_links_selector**: `"a[href*='download']"` - Attachment download links

# The site uses JavaScript navigation (`fnDetailPage()` function) for item links, making it suitable for scrapy-playwright implementation.

# gepaGwangju http://203.251.57.106:82/jwsys_site/gepa/main.html
# stderr 
# I have completed the analysis of the gepaGwangju website using Playwright MCP. The selectors have been extracted and saved to `./items/gepaGwangju.txt`.

# **Summary:**
# - Successfully accessed the gepaGwangju main page
# - Found that the site uses JavaScript-dependent navigation with placeholder links ("#")
# - Extracted CSS selectors based on the observable HTML structure
# - Saved selectors with notes about the site's accessibility limitations

# The created file contains the best-guess selectors based on the page structure, along with important notes about the site's limitations that will need to be addressed when creating the actual spider.

# dcb https://www.dcb.or.kr/01_news/?mcode=0401010000
# stderr 
# DCB 웹사이트 분석이 완료되었습니다. 다음과 같은 CSS 셀렉터들을 추출하여 `./items/dcb.txt` 파일에 저장했습니다:

# - **items_selector**: `"div.board-text table tbody tr"` - 게시물 목록의 각 행
# - **item_title_selector**: `"div.board-text table tbody tr td.link a::text"` - 게시물 제목 텍스트
# - **click_selector**: `"div.board-text table tbody tr td.link a"` - 클릭할 링크 
# - **details_page_url**: `/01_news/?mcode=0401010000&mode=2&no=13980&page=1` - 상세 페이지 URL 예시
# - **details_page_main_content_selector**: `"div.viewBox"` - 상세 페이지 본문 내용
# - **attachment_links_selector**: `"div.view-info ul li a"` - 첨부파일 다운로드 링크

# 이 셀렉터들을 사용하여 Scrapy-Playwright 스파이더를 구현할 수 있습니다.