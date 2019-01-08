from core import Page, Crawler
from custom.parsers.express_article_data_parser import ExpressArticleDataParser

class ArticleCrawler(Crawler):
    def process(self):
        express_article_dp = ExpressArticleDataParser()
        express_article_page = Page(link_source="express_link/articles", path="express_link", dp=express_article_dp, max_data_rows=1000)
        return [express_article_page]

    def post_process(self):
        self.substract_link("express_link/articles", "express_link/all_articles")
        self.add_link("express_link/all_articles", "express_link/articles")