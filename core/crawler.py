import logging
import logging.config
logging.config.fileConfig('logging.conf')

import abc
import time
import os

import core.file

class Crawler:
    def __init__(self, limit=None, timeout=None, loop=False):
        self.file = core.file.File()
        self.page_stack = []
        self.limit = limit
        self.timeout = timeout
        self.loop = loop

    def pre_process(self): pass
    def post_process(self): pass

    def __del__(self):
        self.post_process()

    @abc.abstractmethod
    def process(self):
        pass

    def start(self):
        self.pre_process()
        logging.info("Crawler pre process finished")
        while True:
            self.page_stack = self.process()
            self.set_timeouts()
            i = 0
            while len(self.page_stack) > 0:
                processed = [None] * len(self.page_stack)
                for j in range(len(self.page_stack)):
                    processed[j] = self.page_stack[i % len(self.page_stack)].process()
                    i += 1
                    if self.limit and i >= self.limit: 
                        logging.info("{} links processed".format(i))
                        self.post_process()
                        return
                tmp_stack = []
                for j in range(len(self.page_stack)):
                    if processed[j]: tmp_stack.append(self.page_stack[j])
                self.page_stack = tmp_stack
                logging.info("Crawler one loop processed")
            logging.info("{} links processed".format(i - 1))
            if not self.loop: break
        self.post_process()
        logging.info("Crawler post process finished")



    def set_timeouts(self):
        for page in self.page_stack:
            page.set_timeout(self.timeout)



    def move_link(self, old_path, new_path, prefix=".txt", old_version=1, new_version=1, stop_if_exists=True):
        self.file.move_link(old_path, new_path, prefix, old_version, new_version, stop_if_exists)

    def move_data(self, old_path, new_path, prefix=".csv", old_version=1, new_version=1, stop_if_exists=True):
        self.file.move_data(old_path, new_path, prefix, old_version, new_version, stop_if_exists)

    def get_data_tmp(self, max_rows=1000):
        return self.file.get_data_tmp(max_rows)

    def get_link_tmp(self, max_rows=1000):
        return self.file.get_link_tmp(max_rows)

    def clear_tmp(self, all=False):
        self.file.clear_tmp()

    def substract_link(self, path1, path2, version1=1, version2=1, max_rows=1000, new_path=None, new_version=1):
        path1 = os.path.join("link_sources", path1)
        path2 = os.path.join("link_sources", path2)
        self.file.substract_from_txt(path1, path2, version1, version2, max_rows, new_path, new_version)

    def add_link(self, path1, path2, version1=1, version2=1, max_rows=1000):
        path1 = os.path.join("link_sources", path1)
        path2 = os.path.join("link_sources", path2)
        self.file.add_txt_to_txt(path1, path2, version1, version2, max_rows)
    
    def remove_link(self, path, version=1):
        path = os.path.join("link_sources", path)
        self.file.remove_files(path, ".txt", version)

    def remove_data(self, path, version=1):
        path = os.path.join("data", path)
        self.file.remove_files(path, ".csv", version)