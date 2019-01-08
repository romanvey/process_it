from core import Page, Crawler
from custom.parsers.express_list_link_parser import ExpressListLinkParser
from custom.utils.express_slg import ExpressSLG

class LinkCrawler(Crawler):
    def pre_process(self):
        ExpressSLG(name="article_links", path="express_link").generate()

    def process(self):
        express_list_lp = ExpressListLinkParser()
        express_list_page = Page(link_source="express_link/article_links", path="express_link", lp=express_list_lp)
        return [express_list_page]
