import unittest
from core import DataBlock
from core import RegexSplitter
import logging
logging.basicConfig(filename='logs/file.log',
level=logging.DEBUG,
format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s',
datefmt="%Y-%m-%d %H:%M:%S")

class DataBlockTest(unittest.TestCase):
    def setUp(self):
        pass

    def test_basic_work(self):
        self.db = DataBlock("My  name is Roman really very cool")
        self.db = self.db.divide_into_blocks(RegexSplitter(r"\w+\s\w+"))
        self.db.add_blocks("Vasioko haha")
        self.db.add_column("words", RegexSplitter(r"\w+"))
        self.db.add_column("2char_words", RegexSplitter(r"\w{2}"))
        self.db.add_column("3char_words", RegexSplitter(r"\w{3}"))
        self.db.generate_table()
        self.db.set_save_folder("data")
        self.db.set_name("iraira")
        self.db.save_table(max_rows=10)
        self.assertEqual(self.db.get_column("words"), ['name', 'is', 'Roman', 'really', 'very', 'cool', 'Vasioko', 'haha'])

if __name__ == "__main__":
    unittest.main()