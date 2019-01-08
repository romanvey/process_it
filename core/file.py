import logging
import logging.config
logging.config.fileConfig('logging.conf')

import glob
import pandas as pd
import os
import shutil

class File:
    def __init__(self):
        self.timeout = 1
        self.max_tries = 10
        self.tmp_files = []

    def same_columns(self, df1, df2):
        """
        df1 must have all df2 columns
        """
        df1_cols = list(df1.columns)
        df2_cols = list(df2.columns)
        return len(df1_cols) < 1 or len(df2_cols) < 1 or len(set(df2_cols) - set(df1_cols)) < 1


    def get_files(self, path, prefix="", version=1):
        prefix = "*" + prefix
        logging.info("Get '{}'".format(path))
        files = glob.glob(path + "_" + prefix)
        sizes =  [file.split(path)[1].split(".")[0].split("_")[-1] for file in files]
        versions =  [file.split(path)[1].split(".")[0].split("_")[-2] for file in files]
        new_files = []
        new_sizes = []
        new_versions = []
        for i in range(len(sizes)):
            if sizes[i].isdigit() and versions[i].isdigit() \
            and (version is None or (versions[i] and int(versions[i]) == version)):
                new_sizes.append(int(sizes[i]))
                new_files.append(files[i])
                new_versions.append(int(versions[i]))
        logging.info(new_files)
        if len(new_files) < 1: return [], [], []
        return zip(*sorted(zip(new_sizes, new_files, new_versions)))

    def check_files(self, path, prefix=None, version=1):
        if prefix is None or prefix not in [".csv", ".txt", ""]:
            logging.warning("prefix not selected (valid: '.csv', '.txt', '')")
        _, files, _ = self.get_files(path, prefix, version)
        return len(files) > 0

    def remove_files(self, path, prefix=None, version=1):
        if prefix is None or prefix not in [".csv", ".txt", ""]:
            logging.warning("prefix not selected (valid: '.csv', '.txt', '')")
        _, files, _ = self.get_files(path, prefix, version)
        for file in files:
            os.remove(file)

    def _move_files(self, old_path, new_path, prefix=None, old_version=1, new_version=1, stop_if_exists=True):
        if prefix not in [".csv", ".txt"]:
            logging.warning("prefix not selected (valid: '.csv', '.txt')")
            return
        _, old_files, _ = self.get_files(old_path, prefix, old_version)
        _, new_files, _ = self.get_files(new_path, prefix, new_version)
        if len(old_files) < 1:
            logging.warning("No files with old path")
        if stop_if_exists and len(new_files) > 0:
            logging.warning("New path already exists: ({}, {})".format(new_path, new_version))
            return
        self.remove_files(new_path, prefix, new_version)
        for old_name in old_files:
            new_name = new_path + old_name.split(old_path)[1]
            os.rename(old_name, new_name)

    def move_link(self, old_path, new_path, prefix=".txt", old_version=1, new_version=1, stop_if_exists=True):
        old_path = os.path.join("link_sources", old_path)
        new_path = os.path.join("link_sources", new_path)
        self._move_files(old_path, new_path, prefix, old_version, new_version, stop_if_exists)


    def move_data(self, old_path, new_path, prefix=".csv", old_version=1, new_version=1, stop_if_exists=True):
        old_path = os.path.join("data", old_path)
        new_path = os.path.join("data", new_path)
        self._move_files(old_path, new_path, prefix, old_version, new_version, stop_if_exists)

        
        


    def get_max_file(self, path, prefix=""):
        _, files, _ = self.get_files(path, prefix)
        return files[-1] if len(files) > 0 else None

    def get_max_size(self, path, prefix=""):
        sizes, _, _ = self.get_files(path, prefix)
        return sizes[-1] if len(sizes) > 0 else None

    def get_max_version(self, path, prefix=""):
        _, _, versions = self.get_files(path, prefix, version=None)
        return max(versions) if len(versions) > 0 else None

    def get_lines_from_csv(self, path, start=0, end=None, prefix=".csv", version=1):
        if end is None: end = int(1e10)
        sizes, files, _  = self.get_files(path, prefix, version=version)
        first_idx = 0
        last_idx = len(sizes) - 1
        for i in range(len(sizes)):
            if sizes[i] > start:
                first_idx = i
                break
        for i in range(len(sizes)):
            if sizes[i] > end:
                last_idx = i
                break
        need_rows = end - start

        if len(files) < 1: return pd.DataFrame()

        self.create_lock(files[first_idx])
        out = pd.read_csv(files[first_idx], sep="|")
        self.remove_lock(files[first_idx])
        if end < out.shape[0]:
            return out.iloc[start:end, :]
        out = out.iloc[start:, :]
        need_rows -= out.shape[0]
        for middle_idx in range(first_idx + 1, last_idx):
            self.create_lock(files[middle_idx])
            tmp = pd.read_csv(files[middle_idx], sep="|")
            self.remove_lock(files[middle_idx])
            need_rows -= tmp.shape[0]
            out = pd.concat([out, tmp], axis=0)
        if last_idx == first_idx: return out        
        self.create_lock(files[last_idx])
        tmp = pd.read_csv(files[last_idx], sep="|")
        self.remove_lock(files[last_idx])
        tmp = tmp.iloc[:need_rows, :]
        out = pd.concat([out, tmp], axis=0)
        return out

    def get_lines_from_txt(self, path, start=0, end=None, prefix=".txt", version=1):
        if end is None: end = int(1e10)
        sizes, files, _ = self.get_files(path, prefix, version=version)
        first_idx = 0
        last_idx = len(sizes) - 1
        for i in range(len(sizes)):
            if sizes[i] > start:
                first_idx = i
                break
        for i in range(len(sizes)):
            if sizes[i] > end:
                last_idx = i
                break         
        need_rows = end - start

        if len(files) < 1: return []

        with open(files[first_idx], "r") as f:
            self.create_lock(files[first_idx])
            out = f.read().split("\n")
            self.remove_lock(files[first_idx])
        if end <= len(out):
            return out[start:end+1]
        out = out[start:]
        need_rows -= len(out)
        for middle_idx in range(first_idx + 1, last_idx):
            with open(files[middle_idx], "r") as f:
                self.create_lock(files[middle_idx])
                tmp = f.read().split("\n")
                self.remove_lock(files[middle_idx])
            need_rows -= len(tmp)
            out += tmp
        if last_idx == first_idx: return out
        with open(files[last_idx], "r") as f:
            self.create_lock(files[last_idx])
            tmp = f.read().split("\n")
            self.remove_lock(files[last_idx])
        tmp = tmp[:need_rows]
        out += tmp
        return out

    def create_lock(self, path):
        lock_path = os.path.join("lock", path + ".lock")
        path_elems = os.path.normpath(lock_path).split(os.path.sep)
        if not os.path.exists(lock_path):
            os.makedirs(os.path.join(*path_elems[:-1]), exist_ok=True)
            open(os.path.join(*path_elems), 'w').close()
            return True
        return False

    def get_unlocked_file(self, path, strategy="nearest"):
        # TODO: need implementation and accurate injection in add_data_to_txt/csv
        lock_path = os.path.join("lock", path + ".lock")
        if strategy == "check": return os.path.exists(lock_path)
        if strategy == "wait": return os.path.exists(lock_path)


    def remove_lock(self, path):
        lock_path = os.path.join("lock", path + ".lock")
        if not os.path.exists(lock_path): return False
        path_elems = os.path.normpath(lock_path).split(os.path.sep)
        for i in range(len(path_elems)-1, -1, -1):
            tmp_path = os.path.join(*path_elems[:i+1])
            if i == len(path_elems)-1: os.remove(tmp_path)
            elif not os.listdir(tmp_path): os.rmdir(tmp_path)
            else: break
        return True

    def form_file_name(self, path, version, size, prefix):
        return path + "_" + str(version) + "_" + str(size) + prefix



    def add_data_to_csv(self, path, df, max_rows=1000, prefix=".csv", version=1, check=False, new=False, stop_if_exiests=False):
        if new: version = self.get_max_version(path, prefix) + 1
        sizes, files, _  = self.get_files(path, prefix, version=version)
        if len(files) > 0:
            curr_size = sizes[-1]
            try:
                curr_df = pd.read_csv(files[-1], sep="|")
            except:
                curr_df = pd.DataFrame()
            if stop_if_exiests:
                logging.info("File already exists: {}, skip overriding".format(files[-1]))
                return
        else:
            curr_size = max_rows
            curr_df = pd.DataFrame()
        curr_pos = 0


        if check and not self.same_columns(curr_df, df):
            logging.warning('Column names doesn`t match')
            return

        while curr_pos < df.shape[0]:
            add_pos = max(0, min(max_rows - curr_df.shape[0], df.shape[0]))
            if add_pos > 0:
                curr_df = pd.concat([curr_df, df.iloc[curr_pos:curr_pos+add_pos,:]], axis=0, sort=False)
                path_to_save = self.form_file_name(path, version, curr_size, prefix)
                self.create_folder_structure(path_to_save)
                curr_df.to_csv(path_to_save, sep="|", index=False)
                curr_pos += add_pos
            curr_df = pd.DataFrame()
            curr_size += max_rows

        
    def add_data_to_txt(self, path, lst, max_rows=1000, prefix=".txt", version=1, new=False, stop_if_exiests=False):
        if new: version = self.get_max_version(path, prefix) + 1
        sizes, files, _  = self.get_files(path, prefix, version=version)
        if len(files) > 0:
            curr_size = sizes[-1]
            with open(files[-1]) as f:
                curr_lst = f.read().split("\n")
                if len(curr_lst) == 1 and not curr_lst[0]: curr_lst = []
            if stop_if_exiests:
                logging.info("File already exists: {}, skip overriding".format(files[-1]))
                return
        else:
            curr_size = max_rows
            curr_lst = []
        curr_pos = 0

        while curr_pos < len(lst):
            add_pos = max(0, min(max_rows - len(curr_lst), len(lst)))
            if add_pos > 0:
                curr_lst += lst[curr_pos:curr_pos+add_pos]
                path_to_save = self.form_file_name(path, version, curr_size, prefix)
                self.create_folder_structure(path_to_save)
                with open(path_to_save, "w") as f:
                    for i, line in enumerate(curr_lst):
                        f.write(str(line))
                        if i != len(curr_lst) - 1: f.write("\n")
                curr_pos += add_pos
            curr_lst = []
            curr_size += max_rows

    def create_folder_structure(self, path):
        path_elems = os.path.normpath(path).split(os.path.sep)
        os.makedirs(os.path.join(*path_elems[:-1]), exist_ok=True)
        

    def _get_tmp(self, full_path=["tmp"], prefix=".txt", max_rows=1000):
        version = self.get_max_version(os.path.join(*full_path, "tmp"), prefix=prefix)
        if version is None: version = 0
        else: version += 1
        tmp_file = os.path.join(*full_path, "tmp_" + str(version) + "_" + str(max_rows) + prefix)
        self.create_folder_structure(tmp_file)
        open(tmp_file, 'w').close()
        path = os.path.join(*full_path, "tmp")
        self.tmp_files.append((path, version, prefix))
        return path, version

    def get_link_tmp(self, max_rows=1000):
        return self._get_tmp(full_path=["link_sources", "tmp"], prefix=".txt", max_rows=max_rows)

    def get_data_tmp(self, max_rows=1000):
        return self._get_tmp(full_path=["data", "tmp"], prefix=".csv", max_rows=max_rows)

    def clear_tmp(self, all=False):
        if not all:
            for path, version, prefix in self.tmp_files:
                self.remove_files(path, prefix=prefix, version=version)
        else:
            shutil.rmtree("link_sources/tmp/", ignore_errors=True)
            shutil.rmtree("data/tmp/", ignore_errors=True)


    def substract_from_txt(self, path1, path2, version1=1, version2=1, max_rows=1000, new_path=None, new_version=1):
        lines1 = set(self.get_lines_from_txt(path1, version=version1))
        lines2 = set(self.get_lines_from_txt(path2, version=version2))
        new_lines = list(lines1 - lines2)
        if new_path is None:
            self.remove_files(path1, prefix=".txt", version=version1)
            self.add_data_to_txt(path1, new_lines, max_rows, version=version1)
        else: self.add_data_to_txt(new_path, new_lines, max_rows, version=new_version)
    

    def add_txt_to_txt(self, path1, path2, version1=1, version2=1, max_rows=1000):
        lines_to_add = self.get_lines_from_txt(path2, version=version2)
        self.add_data_to_txt(path1, lines_to_add, max_rows, version=version1)
        