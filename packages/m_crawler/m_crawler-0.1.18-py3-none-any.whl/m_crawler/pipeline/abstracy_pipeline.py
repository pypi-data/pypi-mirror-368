from abc import ABC, abstractmethod
from queue import Queue
from typing import Iterable, Optional, Union

from m_crawler.engine.abstract_request import AbstractRequest
from m_crawler.engine.abstract_response import AbstractResponse
from m_crawler.utils.crawler_exception import AllDataCompletedException


class AbstractPipeline(ABC):

    def __init__(self) -> None:
        self.queue: Queue[Optional[AbstractRequest]] = Queue()

    def proxy_process(
        self, item: Union[AbstractResponse, AllDataCompletedException]
    ) -> None:
        if isinstance(item, AllDataCompletedException):
            self.queue.put(None)
        else:
            process_result = self.process(item)
            if process_result:
                for request in process_result:
                    self.queue.put(request)

    @abstractmethod
    def process(self, item: AbstractResponse) -> Optional[Iterable[AbstractRequest]]:
        """
        处理数据
        """
        pass
