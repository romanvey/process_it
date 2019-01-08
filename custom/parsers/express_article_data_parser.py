from core import Parser, RegexSplitter, DataBlock

class ExpressArticleDataParser(Parser):
    def process(self, text):
        db = DataBlock(text, "content")
        db.add_column("link", RegexSplitter(r'class=\"content\"\ content-iframe>(.*<footer>)', 
        post_processors=["remove_tags", "remove_trailing_spaces"]))
        return [db]