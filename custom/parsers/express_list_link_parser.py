from core import LinkParser, RegexSplitter, DataBlock

class ExpressListLinkParser(LinkParser):
    def process(self, text):
        db = DataBlock(text)
        db.add_column("link", RegexSplitter(r'(https:\/\/expres\.online\/news\/[a-zA-z0-9-]+)\"'))
        return [db]

    def set_sources(self):
        self.set_link_source(0, "link", "articles", check_duplicates=True)