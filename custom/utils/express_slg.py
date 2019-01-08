from utils import SequentialLinksGenerator
class ExpressSLG(SequentialLinksGenerator):
    def start(self): self.data["i"] = 1
    def process(self): return "https://expres.online/news?page={}".format(self.data["i"])
    def step(self): self.data["i"] += 1
    def default_config(self): self.limit = 20