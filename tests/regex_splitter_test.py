import unittest
from core import RegexSplitter

class RegexSplitterTest(unittest.TestCase):
    def setUp(self):
        self.splitter = RegexSplitter("Roma")

    def test_basic_work(self):
        self.assertEqual(self.splitter("Hi! Roma."), ["Roma"])