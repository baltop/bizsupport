"""
Utility functions for the bizsup scrapy project.
"""
import os
import re
from urllib.parse import urljoin, unquote
from typing import Dict, Optional, Union
from playwright.async_api import Page


def abort_request(request):
    """
    Filter unnecessary resource requests to improve scraping performance.
    Used with PLAYWRIGHT_ABORT_REQUEST setting.
    
    Args:
        request: The request object from Playwright
        
    Returns:
        bool: True if the request should be aborted, False otherwise
    """
    return (
        request.resource_type in ["image", "media", "stylesheet"]
        or any(ext in request.url for ext in [".jpg", ".png", ".gif", ".css", ".mp4", ".webm"])
        or "google-analytics.com" in request.url
        or "googletagmanager.com" in request.url
        or "googleapis.com" in request.url
        or "google.com" in request.url
    )


def create_output_directory(output_dir: str) -> None:
    """
    Create output directory if it doesn't exist.
    
    Args:
        output_dir: Path to the output directory
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)


def prepare_attachment_directory(output_dir: str, item_id: str) -> str:
    """
    Create directory for attachments if it doesn't exist.
    
    Args:
        output_dir: Base output directory
        item_id: ID of the item for which to create attachment directory
        
    Returns:
        str: Path to the attachment directory
    """
    attachment_dir = os.path.join(output_dir, item_id)
    if not os.path.exists(attachment_dir):
        os.makedirs(attachment_dir)
    return attachment_dir


def clean_filename(filename: str) -> str:
    """
    Clean up a filename to ensure it's valid for the filesystem.
    
    Args:
        filename: Original filename
        
    Returns:
        str: Cleaned filename
    """
    # First, remove any invalid characters
    filename = re.sub(r'[\\/*?:"<>|]', '', filename)
    
    # Remove excess whitespace
    filename = ' '.join(filename.split())
    
    # Find the extension and make sure it's preserved
    match = re.search(r'\.[a-zA-Z]{2,4}', filename)
    if match:
        # 확장자 위치까지만 포함하여 자름
        return filename[:match.end()]
    return filename  # 확장자가 없으면 원래 문자열 반환

        # # 정규식을 사용하여 .알파벳3글자 형식의 확장자를 찾음
        # match = re.search(r'\.[a-zA-Z]{3,4}', filename)
        # if match:
        #     # 확장자 위치까지만 포함하여 자름
        #     return filename[:match.end()]
        # return filename  # 확장자가 없으면 원래 문자열 반환


def sanitize_filename(self, filename):
    """파일명 정리"""
    # URL 디코딩 (퍼센트 인코딩 제거)
    from urllib.parse import unquote
    filename = unquote(filename)
    
    # 특수문자 제거 (파일 시스템에서 허용하지 않는 문자)
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    # 연속된 공백을 하나로
    filename = re.sub(r'\s+', ' ', filename)
    
    # 너무 긴 파일명 제한
    if len(filename) > 200:
        # 확장자 보존
        name_parts = filename.rsplit('.', 1)
        if len(name_parts) == 2:
            name, ext = name_parts
            filename = name[:200-len(ext)-1] + '.' + ext
        else:
            filename = filename[:200]
            
    return filename



def get_extension_from_content_type(content_type: str) -> str:
    """
    Get file extension from content type.
    
    Args:
        content_type: Content type string from HTTP header
        
    Returns:
        str: File extension including the dot, or empty string if not found
    """
    content_type_map = {
        'application/pdf': '.pdf',
        'application/msword': '.doc',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document': '.docx',
        'application/vnd.ms-excel': '.xls',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': '.xlsx',
        'application/vnd.ms-powerpoint': '.ppt',
        'application/vnd.openxmlformats-officedocument.presentationml.presentation': '.pptx',
        'image/jpeg': '.jpg',
        'image/png': '.png',
        'text/plain': '.txt',
        'application/zip': '.zip',
        'application/x-hwp': '.hwp'
    }
    
    return content_type_map.get(content_type, '')


def extract_filename_from_headers(headers: Dict[str, bytes]) -> Optional[str]:
    """
    Extract filename from Content-Disposition header.
    
    Args:
        headers: HTTP response headers
        
    Returns:
        str or None: Extracted filename or None if not found
    """
    content_disposition = headers.get('Content-Disposition', b'').decode('utf-8', errors='ignore')
    if 'filename=' in content_disposition:
        server_filename = re.search(r'filename="?([^";]+)', content_disposition).group(1)
        return unquote(server_filename)
    return None


def extract_id_from_url(url: str, param_name: str = 'board_seq') -> str:
    """
    Extract ID from URL query parameter.
    
    Args:
        url: URL string
        param_name: Name of the parameter to extract
        
    Returns:
        str: Extracted ID or fallback hash-based ID
    """
    # Look for param_name in query string
    param_match = re.search(fr'{param_name}=([^&]+)', url)
    if param_match:
        return param_match.group(1)
    
    # Fallback to hash of URL
    return f"unknown_{hash(url) % 10000}"


def clean_html(html_content: str) -> str:
    """
    Clean HTML content to plain text for markdown conversion.
    
    Args:
        html_content: HTML content
        
    Returns:
        str: Cleaned text
    """
    if not html_content:
        return ''
    
    # Remove HTML tags
    cleaned = re.sub(r'<[^>]+>', ' ', html_content)
    
    # Remove excess whitespace
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    
    return cleaned


# items_selector에서 tr 이나 ul 을 찾아서 nth-child(index)를 추가하여 생성
def make_selector(items_selector: str, index: int) -> str:
    """
    Create a selector for a specific item by index.
    
    Args:
        items_selector: Base selector for items
        index: Index of the item to select (1-based)
        
    Returns:
        str: Selector for the specific item
    """
    if 'tr' in items_selector:
        selector = re.sub(r'( tr(\.[a-zA-Z0-9_-]+)?)', rf'\1:nth-child({index})', items_selector)
    elif 'li' in items_selector:
        selector = re.sub(r'( li(\.[a-zA-Z0-9_-]+)?)', rf'\1:nth-child({index})', items_selector)
    else:
        raise ValueError("Invalid items_selector format")
    
    return selector





def save_markdown_content(output_dir: str, file_id: str, content: str) -> str:
    """
    Save content as markdown file.
    
    Args:
        output_dir: Output directory
        file_id: ID for the file
        content: Markdown content
        
    Returns:
        str: Path to the saved file
    """
    md_filename = os.path.join(output_dir, f"{file_id}.md")
    with open(md_filename, 'w', encoding='utf-8') as f:
        f.write(content)
    return md_filename


def save_binary_file(path: str, filename: str, data: bytes) -> str:
    """
    Save binary data to a file.
    
    Args:
        path: Directory path
        filename: Filename
        data: Binary data
        
    Returns:
        str: Path to the saved file
    """
    clean_name = clean_filename(filename)
    file_path = os.path.join(path, clean_name)
    
    with open(file_path, 'wb') as f:
        f.write(data)
    
    return file_path



# async def click_and_handle_download(page: Page, selector: str, save_path: str, file_name: str) -> str:
#     try:
#         # 다운로드를 기다리는 context manager 시작 [4]
#         async with page.expect_download() as download_info:
#             # 다운로드를 트리거하는 요소 클릭 (Locators 사용 권장) [4]
#             # Playwright는 액션 수행 전에 요소가 보이고, 안정적인지 등을 자동으로 기다립니다 [8, 9]
#             locator = page.locator(selector) # CSS 또는 XPath 셀렉터 가능 [10]
#             await locator.click() # Playwright Locator click 메서드 사용 [5, 11]

#         # 다운로드 객체 가져오기 [4]
#         download = await download_info.value

#         if re.search(r'\.[a-zA-Z]{2,4}$', download.suggested_filename): 
#             cur_file_name = download.suggested_filename
#         else:
#             cur_file_name = file_name


#         # 파일 저장 경로 설정 (원하는 경로와 다운로드된 파일의 추천 이름 조합) [4]
#         full_save_path = f"{save_path}/{cur_file_name}"

#         # 파일 저장 [4]
#         await download.save_as(full_save_path)

#     except Exception as e:
#         print("click_and_handle_download " + save_path + " " + file_name)
#         print(f"Error occurred: {e}")
#         exit()
#     # 저장된 파일 경로를 결과로 반환 [1]
#     return full_save_path



async def click_and_handle_download(page: Page, selector: str, save_path: str, file_name: str = None) -> str:
    try:
        # 다운로드를 기다리는 context manager 시작
        async with page.expect_download(timeout=20000) as download_info:  # 60초 타임아웃 설정
            # 다운로드를 트리거하는 요소 클릭
            locator = page.locator(selector)
            await locator.click()

        # 다운로드 객체 가져오기
        download = await download_info.value

        # 파일명 처리
        if file_name is None or (download.suggested_filename and re.search(r'\.[a-zA-Z]{2,4}$', download.suggested_filename)):
            cur_file_name = download.suggested_filename
        else:
            cur_file_name = file_name

        # 파일 저장 경로 설정
        full_save_path = f"{save_path}/{cur_file_name}"

        # 파일 저장
        await download.save_as(full_save_path)
        return full_save_path

    except Exception as e:
        # 에러 발생시 종료하지 않고 로그만 남기고 예외를 다시 발생시킴
        print(f"click_and_handle_download error: {save_path} {file_name}")
        print(f"click_and_handle_download error: {e}")
        # raise  # 예외를 다시 발생시켜 호출자에게 알림
        return None  
