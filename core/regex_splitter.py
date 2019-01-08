import logging
import logging.config
logging.config.fileConfig('logging.conf')

from .splitter import Splitter
import re

class RegexSplitter(Splitter):
    
    def __init__(self, pattern, flags=None, post_processors=None):
        if type(pattern) is not str:
            raise TypeError("pattern must be string")
        self.text = pattern
        self.flags = flags if flags else (re.I | re.DOTALL)
        self.regex = re.compile(pattern, flags=self.flags)
        self.post_processors = post_processors if post_processors else []
        self.avaliable_post_processors = ["remove_tags", "remove_trailing_spaces"]

    def __str__(self):
        return self.text

    def __repr__(self):
        return str(self)

    def process(self, text):
        return self._post_process(self.regex.findall(text))

    def _post_process(self, groups_list):
        if len(groups_list) < 1: return []
        if type(groups_list[0]) == tuple: group_list = self.post_process_multiple_groups(groups_list)
        else: group_list = self.post_process_one_group(groups_list)
        return self.general_post_process(self._use_post_processors(group_list))

    def _use_post_processors(self, group_list):
        for post_processor_name in self.post_processors:
            post_processor = self._get_post_processor(post_processor_name)
            if post_processor is None: continue
            for i in range(len(group_list)):
                group_list[i] = post_processor(group_list[i])
        return group_list

    def get_avaliable_post_processors(self):
        return self.avaliable_post_processors

    def _get_post_processor(self, name):
        if name not in self.avaliable_post_processors:
            logging.warning("No such post processor '{}', avaliable: {}".format(name, self.get_avaliable_post_processors))
            return None
        if name == "remove_tags":
            import utils.regex.remove_tags
            return utils.regex.remove_tags
        if name == "remove_trailing_spaces":
            import utils.regex.remove_trailing_spaces
            return utils.regex.remove_trailing_spaces


    def general_post_process(self, group_list):
        return group_list

    def post_process_one_group(self, group_list):
        return group_list

    def post_process_multiple_groups(self, groups_list):
        only_first = []
        for i in range(len(groups_list)):
            only_first.append(groups_list[i][0])
        return only_first

