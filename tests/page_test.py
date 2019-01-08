import unittest
from core import Page
import logging
logging.basicConfig(filename='logs/file.log',
level=logging.DEBUG,
format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s',
datefmt="%Y-%m-%d %H:%M:%S")

class PageTest(unittest.TestCase):
    def setUp(self):
        pass

    def test_creating(self):
        self.page = Page("news")
        self.assertEqual(True, True)
