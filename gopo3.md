# Website Data Extraction Process

This document explains the process for extracting data from paginated website structures with listing and detail pages.

## Input Parameters

For each record to be processed, assign the following fields:

- `start_URL`: {start_URL}
- `site_code`: {site_code}

## Website Structure Understanding

- The `start_URL` represents the first page of a paginated bulletin board structure consisting of listing and detail pages.
- Listing pages typically contain 10-20 items.
- Each listing page has links to access detailed pages for each item.

## Directory Structure Setup

- Create a directory named `coplan` if it doesn't exist already.
- Within `coplan`, create a subdirectory named `{site_code}`.
- All output files will be stored in this subdirectory.

## Process Flow for Each Website

1. **Fetch List Page**
   - Use curl to fetch the `start_URL` and save it as `{site_code}_list.html`:
   ```
   mkdir -p rplan/{site_code}
   curl -s "{start_URL}" -o rplan/{site_code}/{site_code}_list.html
   ```

2. **Extract Detail Page Links**
   - Analyze `{site_code}_list.html` to identify the structure of links to item detail pages.
   - Determine whether links are URL-based or JavaScript-based by inspecting the HTML.

3. **Handle URL-type Links**
   - For URL-type links (where href attributes contain direct URLs):
     - Find the most specific and reliable CSS selector that targets only the detail links.
     - Test the selector by confirming it selects the correct elements in the HTML.
     - Extract a pattern from the URLs to understand their structure.
     - Document a specific example URL for reference.

4. **Handle JavaScript-type Links**
   - For JavaScript links (where onclick attributes contain JavaScript functions):
     - Identify the JavaScript function call pattern and save it.
     - Search for the function definition in the HTML document.
     - If the function definition is not found in the HTML:
       a. Identify all external JavaScript files referenced in the HTML:
          ```
          grep -o '<script [^>]*src="[^"]*"' rplan/{site_code}/{site_code}_list.html | grep -o 'src="[^"]*"' | cut -d'"' -f2
          ```
       b. Download each JavaScript file to the `{site_code}` directory:
          ```
          curl -s "{base_url}{js_file_path}" -o rplan/{site_code}/{js_filename}
          ```
       c. Search each downloaded JavaScript file for the function definition:
          ```
          grep -A 30 "function goBoardView" rplan/{site_code}/{js_filename}
          ```
     - Extract and save the complete function body.

5. **CSS Selector Validation**
   - Always verify selectors exist in the HTML document:
     ```
     grep "class=\"subject\"" rplan/{site_code}/{site_code}_list.html
     ```
   - Test selectors to ensure they extract the correct links:
     ```
     # Example using a tool like pup (if available)
     cat rplan/{site_code}/{site_code}_list.html | pup 'td.subject p.stitle a attr{href}'
     ```

6. **Document Results in Structured Format**
   - Create a markdown file named `{site_code}_link.md` with precise information:

   For URL-based links (example from btp_link.md):
   ```
   list link
   - javascript yes/no: no
   - selector: td.subject p.stitle a
   - link pattern: ?mCode=MN013&mode=view&mgr_seq=16&board_seq=XXXXXXX
   - link example: ?mCode=MN013&mode=view&mgr_seq=16&board_seq=9579787

   - javascript function body: N/A
   - javascript call part: N/A
   ```

   For JavaScript-based links (example from seoul1_link.md):
   ```
   list link
   - javascript yes/no: yes
   - selector: td.left a
   - link pattern: javascript:goBoardView('/user/nd19746.do','View','[0-9]+')
   - link example: javascript:goBoardView('/user/nd19746.do','View','00003825')

   - javascript function body: 
   function goBoardView(url, mode, board_seq) {
       $("#mode").val(mode);
       $("#board_seq").val(board_seq);
       $("#frm").attr("action", url).submit();
   }
   - javascript call part: goBoardView('/user/nd19746.do','View','00003825')
   ```

## Record-by-Record Processing Details

For each website record:

1. Read the start URL and site code from the input record.
2. Create the appropriate directory structure in `coplan/{site_code}`.
3. Download the list page HTML and save as `{site_code}_list.html`.
4. Analyze the HTML to identify the link pattern:
   - Check if links use direct URLs or JavaScript functions.
   - Extract and verify appropriate CSS selectors.
5. For JavaScript-based links:
   - Identify the function call pattern.
   - Extract the function definition from the HTML or external JS files.
   - If not found in the main HTML, download and search all referenced JS files.
6. Document all findings in `{site_code}_link.md` using the structured format.
7. Include complete function definitions when JavaScript links are used.

This systematic approach ensures consistent extraction of navigation patterns across different websites, enabling reliable automated crawling of both listing and detail pages.