import abc
import os
from .parser import Parser

class LinkParser(Parser):
    def __init__(self):
        self._idx = []
        self._cols = []
        self._output = []
        self._check_duplicates = []
        self._save_in_memory = []
        self.blocks = None

    @abc.abstractmethod
    def set_sources(self):
        pass

    def set_link_source(self, idx, col, output, check_duplicates=False, save_in_memory=False):
        self._idx.append(idx)
        self._cols.append(col)
        self._output.append(output)
        self._check_duplicates.append(check_duplicates)
        self._save_in_memory.append(save_in_memory)


    def get_link_sources(self, text):
        self.blocks = self.process(text)
        for block in self.blocks:
            block.generate_table()
        self.set_sources()
        self.out = dict()
        for idx, col, output, check_dup, memory in zip(self._idx, self._cols, self._output, self._check_duplicates, self._save_in_memory):
            if self.blocks[idx].df.shape[0] == 0: continue
            links = list(self.blocks[idx].df[col])
            self.out[output] = (links, check_dup, memory)
        return self.out

    def __call__(self, text):
        return self.get_link_sources(text)
