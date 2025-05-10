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
    match = re.search(r'\.[a-zA-Z0-9]{2,4}$', filename)
    if match:
        # Truncate filename if it's too long, but preserve the extension
        max_length = 100  # Adjust as needed
        if len(filename) > max_length:
            extension = filename[match.start():]
            filename = filename[:max_length-len(extension)] + extension
    
    return filename.strip()


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
        return items_selector.replace('tr', f'tr:nth-child({index})')
    elif 'li' in items_selector:
        return items_selector.replace('li', f'li:nth-child({index})')
    else:
        raise ValueError(f"Invalid items_selector format: {items_selector}")


async def click_and_handle_download(page: Page, selector: str, save_path: str) -> str:
    """
    Click a download link and save the downloaded file.
    
    Args:
        page: Playwright page object
        selector: CSS selector for the download link
        save_path: Directory path to save the file
        
    Returns:
        str: Path to the saved file
    """
    # Wait for download to start
    async with page.expect_download() as download_info:
        # Click the download link
        locator = page.locator(selector)
        await locator.click()

    # Get download object
    download = await download_info.value
    
    # Generate save path with suggested filename
    filename = download.suggested_filename
    clean_name = clean_filename(filename)
    full_save_path = os.path.join(save_path, clean_name)
    
    # Save the file
    await download.save_as(full_save_path)
    
    return full_save_path


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