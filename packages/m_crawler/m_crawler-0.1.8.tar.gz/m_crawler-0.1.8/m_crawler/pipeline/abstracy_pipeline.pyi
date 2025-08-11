import abc
from abc import ABC, abstractmethod
from m_crawler.engine.abstract_request import AbstractRequest as AbstractRequest
from m_crawler.engine.abstract_response import AbstractResponse as AbstractResponse
from m_crawler.scheduler.scheduler import Scheduler as Scheduler
from typing import Iterable

class AbstractPipeline(ABC, metaclass=abc.ABCMeta):
    schedulers: set[Scheduler] | None
    def __init__(self) -> None: ...
    def register_scheduler(self, scheduler: Scheduler) -> None: ...
    def process(self, item: AbstractResponse | None) -> None: ...
    @abstractmethod
    def process_item(self, item: AbstractResponse | None) -> Iterable[AbstractRequest | None]: ...
