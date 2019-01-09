# PROCESSit

- core/ - all core components
- utils/ - all additional components
- data/ - located parsed csvs
- link_sources/ - located files with links
- tests/ - located test files
- envs.py - for testing Regex
- utils.py - for doing some stuff related to utils
- main.py - for running custom crawlers
- custom/ - located all custom scripts
- tmp/ - generated temporary files, like html page
- logs/ - generated logs
- logging.conf - logger file
- README.md - documentation file

# Features:
- Scheduler, you can specify when you want to parse data
- Split large files into small
- Can work with multiple files like with one
- Crawler could be started in different threads, because scheduler works with them by default
- Flexible, because project divided into small logical components
- Tools for writting correct and fast regex queries
- Additional post processors for regex like "remove trailling spaces" and "remove tags and content inside" for faster work
- Logging system for checking progress in real-time
- Fault tolerant, can handle: empty link file, not valid link, not founded data, unexpected exit etc.
- Can check for duplicates, so you can run it in loop and module will add only new data
- Can work with different scenarios: check one page with some interval (for example, get Apple prices every minute), iterate through links to get more links and after that parse them (for example, some sites have pages with links to articles) or iterate through pages and parse them in one step (for example, some pages have links to next pages)

# Example:
##### In main.py located example, which can crawl in 3 steps:
1) Generate links, where located all article links (link_sources/express_link/article_links)
2) Parse every this link to get article link (link_sources/express_link/articles)
3) Parse every article link to get news content(data/express_link/content)

##### For this task we only need 6 files:
custom/crawlers/article_crawler.py
custom/crawlers/link_crawler.py
custom/parsers/express_article_data_parser.py
custom/parsers/express_list_link_parser.py
custom/utils/express_slg.py
main.py

# Future work:
- Add server-client component which can send data to user and get from him labled data
- Additional data processing utils
- Dynamic page loader for scrapping sites with JS
- Additional functions for Page class
- Site with documentation
- Publish
- More examples
