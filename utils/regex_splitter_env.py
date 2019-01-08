from .page_loader import PageLoader
from core import RegexSplitter
import webbrowser
from subprocess import Popen, PIPE
from datetime import datetime
import os
import logging
import shutil

class RegexSplitterEnv:
    """
    Use re.findall() function inside, look for documentation how it works
    """
    def __init__(self, regex=None, text=None, url=None, clear=False, write_to_tmp=True, **kwargs):
        self.text = text
        self.write_to_tmp = write_to_tmp
        if url: self.load_page(url)
        self.regex = RegexSplitter(regex, **kwargs)
        self.clear = clear

    def __del__(self):
        if self.clear: self.clear_tmp()

    def load_page(self, url):
        self.url = url
        self.text = PageLoader(url).load()
        if self.text is None:
            logging.warning("Url not parsed")
            os._exit(0)

    def set_text(self, text):
        self.text = text

    def set_regex(self, regex):
        self.regex = RegexSplitter(regex)
    
    def test(self, limit=None, verbose=True):
        out = self.regex(self.text)
        if limit is None: limit = len(out)
        if verbose: 
            for i, match in enumerate(out[:limit]):
                print(i + 1, "MATCH")
                print(match)
            if len(out) < 1: print("NO MATCHES!")
        return out[:limit]

    def test_gui(self, times=2, open_link=True, write_to_tmp=True):
        to_show = "REGEX: " + str(self.regex) + "\n"
        to_show += ("URL: " + self.url + "\n") if self.url else ""
        to_show +=  self.text
        dt = datetime.now()
        write_to_tmp = write_to_tmp if write_to_tmp else self.write_to_tmp
        if write_to_tmp:
            if not os.path.exists("tmp/"): os.makedirs("tmp/")
            f = open("tmp/" + str(dt) + ".txt", "w")
            f.write(to_show)
            f.close()
        try:
            p = Popen(['xsel','-bi'], stdin=PIPE)
            p.communicate(input=to_show.encode('utf-8'))
        except: logging.warning("xsel not found. Clipboard ignored!")
        for _ in range(times): webbrowser.open("https://regex101.com/")
        if self.url and open_link: webbrowser.open(self.url)

    def clear_tmp(self):
        shutil.rmtree('tmp', ignore_errors=True)
