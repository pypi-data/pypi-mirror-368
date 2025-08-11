from bs4 import BeautifulSoup


class Parser:
    __solts__ = ("soup",)

    def __init__(self, content: str) -> None:
        self.soup = BeautifulSoup(content, "lxml")
