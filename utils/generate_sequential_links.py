import logging
import logging.config
logging.config.fileConfig('logging.conf')

import core.file
import os
import abc

class SequentialLinksGenerator:
    def __init__(self, name="default", path="", limit=100, max_rows=100000, new=False, stop_if_exists=False, version=1):
        self.file = core.file.File()
        self.path = os.path.join("link_sources", path)
        self.name = name
        self.limit = limit
        self.data = dict()
        self.max_rows =  max_rows
        self.new = new
        self.stop_if_exists = stop_if_exists
        self.version = version

    def set_path(self, path):
        self.path = os.path.join("link_sources", path)

    @abc.abstractmethod
    def start(self):
        pass

    @abc.abstractmethod
    def process(self):
        pass

    @abc.abstractmethod
    def step(self):
        pass

    @abc.abstractmethod
    def default_config(self):
        pass

    def generate(self):
        links = []
        self.default_config()
        self.start()
        for i in range(self.limit):
            links.append(self.process())
            self.step()
        path = os.path.join(self.path, self.name)
        if self.file.check_files(path, ".txt", self.version) and not self.stop_if_exists:
            self.file.remove_files(path, ".txt", self.version)
        self.file.add_data_to_txt(path, links, max_rows=self.max_rows, new=self.new, stop_if_exiests=self.stop_if_exists)
        logging.info("links generated")