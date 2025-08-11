from queue import Empty, Queue
import threading
from loguru import logger
from typing_extensions import Optional

from m_crawler.engine.abstract_request import AbstractRequest


class Scheduler:
    __slots__ = (
        "queue",
        "seen_urls",
        "max_retry_count",
        "__no_more_data_flag",
        "__retry_dict",
    )
    lock = threading.Lock()

    def __init__(self, max_retry_count: int = 3) -> None:
        self.queue: Queue[Optional[AbstractRequest]] = Queue()
        self.seen_urls: set[str] = set()
        self.max_retry_count = max_retry_count
        self.__retry_dict: dict[str, int] = {}
        self.__no_more_data_flag: bool = False

    def seen(self, url: str) -> bool:
        if url in self.seen_urls:
            return True
        with Scheduler.lock:
            if url in self.seen_urls:
                return True
            self.seen_urls.add(url)
            return False

    def push(self, req: Optional[AbstractRequest]) -> None:
        if req is None:
            self.queue.put(None)
        if req and not self.seen(req.url):
            self.queue.put(req)
            self.seen_urls.add(req.url)

    def pop(self) -> Optional[AbstractRequest]:
        try:
            return self.queue.get(block=True, timeout=30.0)
        except Empty as e:
            logger.error(e)
            return None

    def push_retry(self, req: AbstractRequest) -> bool:
        # 检测是否已经达到重试的最大次数
        with Scheduler.lock:
            if self.__retry_dict.get(req.url, 0) >= self.max_retry_count:
                return False
            self.seen_urls.remove(req.url)
            self.__retry_dict[req.url] = self.__retry_dict.get(req.url, 0) + 1
            self.queue.put(req)
            return True

    @property
    def no_more_data(self) -> bool:
        return self.__no_more_data_flag

    @no_more_data.setter
    def no_more_data(self, flag: bool) -> None:
        """
        标识当前调度器外部的数据已经接收完毕，需要外部数据结束后调用此方法通知
        """
        self.__no_more_data_flag = flag
