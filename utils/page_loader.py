from urllib.request import urlopen
import time

class PageLoader:
    def __init__(self, url=None, timeout=None):
        self.url = url
        self.timeout = timeout
    
    def load(self, url=None):
        url = url if url is not None else self.url
        try:
            text = urlopen(url).read().decode('utf-8')   
        except:
            try:
                text = urlopen(url).read().decode('CP1251')            
            except: return None
        if self.timeout: time.sleep(self.timeout)
        return text

    def set_timeout(self, timeout):
        self.timeout = timeout