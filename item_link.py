# -*- coding: utf-8 -*-
import csv
import subprocess
import os
import sys
import time


# 이 스크립트는 사이트 코드와 URL이 포함된 CSV 파일을 읽고, 셸에서 실행할 명령어를 생성하여 실행합니다.
# 이 명령어는 Playwright를 사용해 웹 페이지의 페이지네이션 링크를 찾기 위해 설계되었습니다.

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
        if index <= 68:
            continue
        if index > 88:
            break
        print(row[0], row[2])  # Replace 0 with the index of the desired field (e.g., site_code column index)

        com = (f"claude --dangerously-skip-permissions -p '{row[0]}의 URL {row[2]}에 playwright mcp를 이용같은 접근한다. url은 item들의 목록을 표시하는 list page 이다. 각 item의 link를 클릭하면 item 상세 페이지로 이동한다. "
                " scrapy-playwright  spider코드에서 링크를 클릭하기 위해 다음 샘플과 같은 item 목록 링크의 css selector와 텍스트를 가져오기 위한 "
                " css selector가 판별되어야 한다. ￦n "
                " 샘플 :     items_selector = \"table.bbs-list tbody tr\" \n"
                "            item_title_selector = \"table.bbs-list tbody tr td.align_left a div span::text\" \n"
                "            click_selector = \"table.bbs-list tbody tr td.align_left a\" \n" 
                " 실제로 click_selector를 클릭하면 item의 상세 페이지로 이동해야 한다. "
                " 이동한 후에 item 상세페이지의 url을 저장한다. \n"
                " 샘플      details_page_url = \"/board_detail?id=829\" \n"
                " item 상세페이지에서 본문을 저장하기 위해 공고 를 표시하는 css selector를 추출해야 한다. item 상세페이지에는 대개 첨부파일 링크가 있는데 "
                " 그부분을 클릭해서 파일을 다운로드 받을 수 있는 첨부파일 링크의 css selector도 추출해야 한다. 아래 샘플을 참고 할 것. \n"
                " 샘플      details_page_main_content_selector = \"div#content\" \n"
                "            attachment_links_selector = \"table.bbs-view tbody tr td ul li a\" \n"
                " 추출된 내용은 ./items/사이트코드.txt 형식으로 저장한다. \n"
                " 파일 내용은 다음과 같은 형식으로 한다. \n"
                "--- 파일 저장 샘플 \n"
                "items_selector = \"table.bbs-list tbody tr\" \n"
                "item_title_selector = \"table.bbs-list tbody tr td.align_left a div span::text\" \n"
                "click_selector = \"table.bbs-list tbody tr td.align_left a\" \n"
                "details_page_url = \"/board_detail?id=829\" \n"
                "details_page_main_content_selector = \"div#content\" \n"
                "attachment_links_selector = \"table.bbs-view tbody tr td ul li a\" \n"
                "--- \n'" )
        

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
