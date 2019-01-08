import unittest
import core.file
import logging
logging.basicConfig(filename='logs/file.log',
level=logging.DEBUG,
format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s',
datefmt="%Y-%m-%d %H:%M:%S")

class FileTest(unittest.TestCase):
    def setUp(self):
        self.file = core.file.File()

    def test_remove_lock(self):
        self.assertEqual(self.file.remove_lock("data/data"), True)

    def test_create_lock(self):
        self.assertEqual(self.file.create_lock("data/data"), True)


    def test_get_lines(self):
        self.assertEqual(self.file.get_lines_from_txt("data/data", end=214)[-1], "|kurka||1")

    def test_saving_csv(self):
        df = self.file.get_lines_from_csv("data/data", start=10, end=200)
        self.file.add_data_to_csv("data/new_data", df, max_rows=20)
        self.assertTrue(True)

    def test_saving_txt(self):
        lst = self.file.get_lines_from_txt("data/data", end=200)
        self.file.add_data_to_txt("data/new_data", lst, max_rows=50)
        self.assertTrue(True)

if __name__ == "__main__":
    pass
