import logging
import logging.config
logging.config.fileConfig('logging.conf')

import os
from .file import File
from utils.page_loader import PageLoader

class Page:
    def __init__(self, link_source = None, path = "", \
    url=None, dp=None, lp=None, use_same_url=False, loader=None,\
    data_version=1, link_version=1, source_version=1, remove_duplicates=True, timeout=None,\
    data_to_new=False, link_to_new=False, max_data_rows=1000, max_link_rows=1000):
        self.file = File()
        self.timeout = timeout
        self.page_loader = PageLoader(timeout=timeout) if loader is None else loader

        self.data_parser = dp
        self.link_parser = lp

        self.data_version = data_version
        self.link_version = link_version
        self.source_version = source_version

        self.set_data_path(path)
        self.set_link_path(path)

        self.use_same_url = False
        self.remove_duplicates = remove_duplicates

        self.data_blocks = []
        self.link_blocks = []
        self.raw_data = None
        self.tags = None

        self.data_to_new = data_to_new
        self.link_to_new = link_to_new


        self._url_already_given = False
        self._link_source_load_idx = 0
        self._link_source_pos = 0
        self._has_url = True

        if url is None and use_same_url: 
            logging.warning("for using 'use_same_url' argument use 'url' argument too")

        if url is not None:
            self._url_already_given = True
            self.url = url
            self.use_same_url = use_same_url 


        self.link_source = os.path.join("link_sources", link_source)
        self.max_links_from_source = 20000
        self.links = []

        self.max_data_rows = max_data_rows
        self.max_link_rows = max_link_rows
        self.cached_links = dict()

    def set_timeout(self, timeout):
        self.timeout = timeout
        self.page_loader.set_timeout(self.timeout)

    def get_new_url(self):
        if self.use_same_url: return
        if self._url_already_given:
            self._url_already_given = False
            return
        if self._link_source_pos >= len(self.links):
            self.get_next_links()
            self._link_source_pos = 0
        if self._link_source_pos >= len(self.links): self.url = None
        else: self.url = self.links[self._link_source_pos]
        self._link_source_pos += 1


    def get_next_links(self):
        self.links = self.file.get_lines_from_txt(self.link_source,
        start=self._link_source_load_idx,
        end=self._link_source_load_idx + self.max_links_from_source, version=self.source_version)
        self._link_source_load_idx += len(self.links)
        if len(self.links) < 1:
            self._has_url = False

    def load_page(self):
        data = self.page_loader.load(self.url)
        while data is None:
            self.get_new_url()
            if not self._has_url or (data is None and self.use_same_url): return False
            data = self.page_loader.load(self.url)
        logging.info("Parsed: {}".format(self.url))
        self.raw_data = data
        return True

    def process(self):
        self.get_new_url()
        if not self.load_page(): return False
        if self.data_parser:
            self.data_blocks = self.data_parser(self.raw_data)
            for block in self.data_blocks:
                block.set_save_folder(self.data_path)
                block.add_tags(self.tags)
                block.generate_table()
                block.save_table(max_rows=self.max_data_rows, version=self.data_version, new=self.data_to_new)

        if self.link_parser:
            self.link_blocks = self.link_parser(self.raw_data)
            for path in self.link_blocks:
                curr_links, check_dup, memory = self.link_blocks[path]
                path_to_link = os.path.join(self.link_path, path)
                
                if self.remove_duplicates:
                    curr_links = list(set(curr_links))

                if check_dup:
                    if (path_to_link, self.link_version) not in self.cached_links:
                        self.cached_links[(path_to_link, self.link_version)] = set(self.file.get_lines_from_txt(path_to_link, version=self.link_version))
                    curr_links = list(set(curr_links) - self.cached_links[(path_to_link, self.link_version)])
                    if not memory:
                        del(self.cached_links[(path_to_link, self.link_version)])
                
                self.file.add_data_to_txt(path_to_link, curr_links, \
                max_rows=self.max_link_rows, version=self.link_version, new=self.link_to_new)
        return True

    def set_data_parser(self, parser):
        self.data_parser = parser

    def set_link_parser(self, parser):
        self.link_parser = parser

    def add_tags(self, tagname):
        if type(tagname) is str: self.tags.add(tagname)
        else: self.tags.update(tagname)

    def set_data_path(self, path):
        self.data_path = os.path.join("data", path)

    def set_link_path(self, path):
        self.link_path = os.path.join("link_sources", path)

    def move_link(self, old_path, new_path, prefix=".txt", old_version=None, new_version=1, stop_if_exists=True):
        old_version = old_version if old_version else self.link_version
        self.file.move_link(old_path, new_path, prefix, old_version, new_version, stop_if_exists)

    def move_data(self, old_path, new_path, prefix=".csv", old_version=None, new_version=1, stop_if_exists=True):
        old_version = old_version if old_version else self.data_version
        self.file.move_data(old_path, new_path, prefix, old_version, new_version, stop_if_exists)

    def get_data_tmp(self, max_rows=None):
        max_rows = max_rows if max_rows is not None else self.max_data_rows
        return self.file.get_data_tmp(max_rows)

    def get_link_tmp(self, max_rows=None):
        max_rows = max_rows if max_rows is not None else self.max_link_rows
        return self.file.get_link_tmp(max_rows)

    def clear_tmp(self, all=False):
        self.file.clear_tmp()

    def substract_link(self, path1, path2, version1=None, version2=None, max_rows=None, new_path=None, new_version=1):
        version1 = version1 if version1 else self.link_version
        version2 = version2 if version2 else self.link_version
        path1 = os.path.join("link_sources", path1)
        path2 = os.path.join("link_sources", path2)
        max_rows = max_rows if max_rows is not None else self.max_link_rows
        self.file.substract_from_txt(path1, path2, version1, version2, max_rows, new_path, new_version)

    def add_link(self, path1, path2, version1=None, version2=None, max_rows=None):
        version1 = version1 if version1 else self.link_version
        version2 = version2 if version2 else self.link_version
        path1 = os.path.join("link_sources", path1)
        path2 = os.path.join("link_sources", path2)
        max_rows = max_rows if max_rows is not None else self.max_link_rows
        self.file.add_txt_to_txt(path1, path2, version1, version2, max_rows)
    
    def remove_link(self, path, version=None):
        version = version if version else self.link_version
        path = os.path.join("link_sources", path)
        self.file.remove_files(path, ".txt", version)

    def remove_data(self, path, version=None):
        version = version if version else self.data_version    
        path = os.path.join("data", path)
        self.file.remove_files(path, ".csv", version)

    