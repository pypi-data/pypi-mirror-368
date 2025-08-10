from bs4 import BeautifulSoup


class Parser:
    __solts__ = ("soup",)

    def __init__(self, context: str) -> None:
        self.soup = BeautifulSoup(context, "lxml")
