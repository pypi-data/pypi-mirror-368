from abc import ABC, abstractmethod
from typing import Iterable, Optional, Set

from m_crawler.engine.abstract_request import AbstractRequest
from m_crawler.engine.abstract_response import AbstractResponse
from m_crawler.scheduler.scheduler import Scheduler


class AbstractPipeline(ABC):

    def __init__(self) -> None:
        self.schedulers: Optional[Set[Scheduler]] = None

    def register_scheduler(self, scheduler: Scheduler) -> None:
        if self.schedulers is None:
            self.schedulers = set()
        self.schedulers.add(scheduler)

    def process(self, item: Optional[AbstractResponse]) -> None:
        process_result = self.process_item(item)
        if self.schedulers:
            for scheduler in self.schedulers:
                for request in process_result:
                    if request:
                        scheduler.push(request)

    @abstractmethod
    def process_item(
        self, item: Optional[AbstractResponse]
    ) -> Iterable[Optional[AbstractRequest]]:
        """
        处理 engine 获取的数据
        """
        pass
