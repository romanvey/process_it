import abc

class Parser:
    def __init__(self):
        pass

    def __call__(self, text):
        return self.process(text)

    @abc.abstractmethod
    def process(self, text):
        pass