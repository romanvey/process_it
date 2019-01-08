import logging
import logging.config
logging.config.fileConfig('logging.conf')

import pandas as pd
from math import isnan
import os
from .file import File

class DataBlock:
    def __init__(self, text, name="default", save_folder="data", tags=None, add_block_column=True, increment_block=True, version=1):
        if type(text) is str: self.blocks = [text]
        else: self.blocks = text
        self.file = File()
        self.df = pd.DataFrame()
        self.tags = set() if tags is None else set(tags)
        self.save_folder = save_folder
        self.name = name
        self._col_names = []
        self._col_funcs = []
        self._col_dtypes = []
        self.add_block_column = add_block_column
        self.increment_block = increment_block

        self._apply_col = []
        self._apply_func = []
        self.version = version

    def _parse_all_blocks(self, func):
        out = []
        for block in self.blocks:
            out += func(block)
        return out

    def divide_into_blocks(self, func):
        return DataBlock(self._parse_all_blocks(func))

    def sort_blocks(self, sort_key, inverse=False):
        if inverse:
            self.blocks = self.blocks[::-1]
        elif callable(sort_key):
            self.blocks.sort(key=sort_key)
        elif type(sort_key) in [list, range]:
            tmp_blocks = [None] * len(self.blocks)
            for i in range(sort_key):
                tmp_blocks[sort_key[i]] = self.blocks[i]
            self.blocks = tmp_blocks


    def add_column(self, name, func, dtype="string"):
        if name in self._col_names:
            raise AttributeError("Column name already exists!")
        if name == "block":
            raise AttributeError("'block' reserved column name!")
        self._col_names.append(name)
        self._col_funcs.append(func)
        self._col_dtypes.append(dtype)

    def get_column(self, name, filter_nans=True):
        if name not in list(self.df.columns): return []
        if filter_nans: return [e for e in list(self.df[name]) if (type(e) != float or not isnan(e))]
        else: return list(self.df[name])

    def add_blocks(self, text):
        if type(text) is str: self.blocks += [text]
        else: self.blocks += text

    def apply_to_block(self, func):
        for i in range(len(self.blocks)):
            self.blocks[i] = func(self.blocks[i])

    def apply_to_column(self, name, func):
        self._apply_col.append(name)
        self._apply_func.append(func)


    def add_tags(self, tagname):
        if tagname is None: return
        if type(tagname) is str: self.tags.add(tagname)
        else: self.tags.update(tagname)

    def set_save_folder(self, save_folder):
        self.save_folder = save_folder

    def set_name(self, name):
        self.name = name

    def save_table(self, path=None, max_rows=100000, version=None, check=True, new=False):
        version = version if version else self.version
        if path is None: path = os.path.join(self.save_folder, self.name)
        logging.info(self.df.shape)
        if self.df.shape[0] != 0:
            if self.add_block_column and self.increment_block:
                curr_max_file = self.file.get_max_file(path, ".csv")
                try: to_add = pd.read_csv(curr_max_file, sep="|")["block"].max() + 1
                except: to_add = 0
                self.df["block"] += to_add
            self.file.add_data_to_csv(path, self.df, max_rows=max_rows, version=version, check=check, new=new)
        else:
            logging.warning("DataFrame is empty!")


    def generate_table(self):
        for idx, block in enumerate(self.blocks):
            tmp_df = pd.DataFrame()
            for name, func, dtype in zip(self._col_names, self._col_funcs, self._col_dtypes):
                rows = func(block)
                col_names = list(tmp_df.columns) + [name]
                tmp_df = pd.concat([tmp_df, pd.DataFrame(rows)], ignore_index=True, axis=1, sort=False)                
                if tmp_df.shape[0] == 0: continue
                tmp_df.columns = col_names
            if self.add_block_column: tmp_df["block"] = idx
            self.df = pd.concat([self.df, tmp_df], axis=0)
        if self.df.shape[0] == 0: return
        self.df.columns = self._col_names + (["block"] if self.add_block_column else [])
                
        for name, dtype in zip(self._col_names, self._col_dtypes):
            if dtype == "int":
                self.df[name] = pd.to_numeric(self.df[name], errors="coerce")
            elif dtype != "string":
                self.df[name] = self.df[name].astype(dtype)
        if self.add_block_column: self.df["block"] = pd.to_numeric(self.df["block"], errors="coerce")

        for col, apply_func in zip(self._apply_col, self._apply_func):
            self.df[col] = self.df[col].apply(apply_func)