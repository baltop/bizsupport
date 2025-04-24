    # Codebase Overview

    Here’s a high-level overview of what you’ve got in this repo:

    1. Top-level files
       - scrapy.cfg — Scrapy project config (points to bizsup.settings)
       - server_full.csv — Master list of sites to crawl (columns: site code, name, start URL, API flag)
       - btp_output/… — Output folder populated by the `btp` spider (Markdown files + any attachments)
       - *.md, *.html, download_links.txt, etc. — Misc. sample pages, extracted links, chat-log artifacts

    2. The Scrapy project “bizsup”
       - bizsup/settings.py
         * BOT_NAME, SPIDER_MODULES, Playwright download handlers for JS-heavy pages
         * Per-domain download slot overrides (e.g. btp.or.kr)
         * UTF-8 feed encoding, async reactor, custom USER_AGENT
       - bizsup/items.py & bizsup/pipelines.py
         * Stub templates (items aren’t strongly typed; pipelines are basically no-ops)
       - bizsup/middlewares.py
         * Default spider/downloader middleware skeleton (unused custom logic)

    3. Spiders (bizsup/spiders/*.py)
       You have one spider per “site code” (matching server_full.csv). Each spider typically does:
       - `start_requests()` → fetch the list page (using `playwright: True` where JS links need clicking)
       - `parse()` → select the table or list of notices, skip notices/headers, extract ID, title, detail URL
       - Pagination up to a hard cap (usually 3 pages)
       - For each notice → `parse_detail()`
           * Extract the HTML content, “clean” it to Markdown (strip tags, preserve breaks)
           * Write `OUTPUT_DIR/<notice_id>.md`
           * Find attachment links, then yield requests to `save_attachment()`
       - `save_attachment()` → handles Korean filenames (via `unquote`), infers extension from Content-Type, writes
    bytes to disk

    4. Outputs & artifacts
       - Each spider writes into its own `OUTPUT_DIR` (e.g. `btp_output/…`)
       - The repo already contains the `btp_output` dump from a run of the `btp` spider
       - There are also sample HTML snapshots (e.g. itp_page.html) and link dumps to aid debugging

    5. How to run
       - `scrapy crawl <sitecode>` (e.g. `scrapy crawl btp`)
       - Spiders are wired to stop after 3 pages by default
       - Uses Scrapy-Playwright for any JavaScript-driven navigation (click links, download popups)

    In short, this is a multi-site Scrapy/Playwright scraper. It iterates over a registry of “tech-park” or
    business-support agency websites, scrapes their announcement listings, saves each announcement as Markdown, and
    grabs any attached files. Let me know if you’d like to dive into any particular spider or component in more detail!
    *** End Patch
