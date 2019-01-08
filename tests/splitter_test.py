import unittest
from core import Splitter

class SplitterTest(unittest.TestCase):
    def setUp(self):
        self.splitter = Splitter(lambda x: x.split(" "))

    def test_basic_work(self):
        self.assertEqual(self.splitter("Hi! Roma."), ["Hi!", "Roma."])