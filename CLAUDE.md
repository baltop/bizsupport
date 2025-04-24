# Scrapy Project Guidelines

## Commands
- Run spider: `scrapy crawl <spider_name>` (from project directory)
- Run single spider with output: `scrapy crawl <spider_name> -o output.json`
- Create new spider: `scrapy genspider <spider_name> <domain>`
- Shell for testing selectors: `scrapy shell <url>`
- Check spider: `scrapy check <spider_name>`
- List spiders: `scrapy list`

## Code Style
- **Imports**: Standard library first, then third-party, then local (alphabetical)
- **Classes**: CamelCase naming
- **Methods/Functions**: snake_case naming
- **Constants**: UPPERCASE with underscores
- **Indentation**: 4 spaces, no tabs
- **Line Length**: Max 100 characters
- **Error Handling**: Use try/except only when necessary, prefer specific exceptions
- **Spider Methods**: Follow Scrapy conventions (parse, parse_item, etc.)
- **Documentation**: Docstrings for spiders and complex methods
- **Type Hints**: Use for function parameters and return values

## Project Outline
- Read the server_full.csv file and generate one Scrapy spider code for each record.

- Each record consists of the following data: 사이트코드 (site code), 기관명 (institution name), start_URL, and API_yn.

- Set the spider's name to the 사이트코드 and name the Python file as {사이트코드}.py.

- Extract the domain from the start_URL field.

- The ultimate goal of each spider is to parse the HTML file fetched from the start_URL to identify a list of announcements. Then, it should visit the detail page of each announcement, save the announcement content as a Markdown file, and if there are any attachments, download and save them.

## Project Structure
- Keep spiders in spiders/ directory
- Do not modify bizsup/items.py, bizsup/pipelines.py, bizsup/settings.py and bizsup/middlewares.py
- Do create spiders or edit exist spiders.
- Before create spiders, always analysis the html structure of starting page and item page to get the selectors.
- Using fetch mcp, get the starting html page. If failed, stop the task. Do not create relevant spiders.
- There is 2 type of spiders. one is url link style and the other is javascript link style.
- As first starting page has javascript link, use javascript templete spider and scrapy-playwright.

