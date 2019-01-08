import logging
import logging.config
logging.config.fileConfig('logging.conf')

from core import Scheduler
from custom.crawlers.link_crawler import LinkCrawler
from custom.crawlers.article_crawler import ArticleCrawler



link_crawler = LinkCrawler(timeout=10)
article_crawler = ArticleCrawler(timeout=10)
scheduler = Scheduler()

def crawl_news():
    link_crawler.start()
    logging.info("Articles collected")
    article_crawler.start()
    logging.info("Articles parsed")

    

#print(scheduler.add_at_specific_time("08/01/2019 18:30:00", crawl_news, repeat="00:06:00", name="Crawl news")
scheduler.add_from_now("00:00:05", crawl_news, repeat="00:06:00", name="Crawl news")
scheduler.start()