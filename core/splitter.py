class Splitter:
    def __init__(self, func):
        self.process = func

    def __call__(self, text):
        return self.process(text)