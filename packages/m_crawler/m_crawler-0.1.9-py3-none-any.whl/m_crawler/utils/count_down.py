import threading


class CountDown:
    __slots__ = "__count"
    __lock = threading.Lock()

    def __init__(self, count: int = 0) -> None:
        self.__count = count

    def count_down(self) -> bool:
        with CountDown.__lock:
            if self.__count <= 0:
                return True
            return False

    def add(self) -> None:
        with CountDown.__lock:
            self.__count += 1

    def down(self) -> None:
        with CountDown.__lock:
            self.__count -= 1
