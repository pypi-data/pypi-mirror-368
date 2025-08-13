import abc
from abc import ABC, abstractmethod
from m_crawler.engine.abstract_request import AbstractRequest as AbstractRequest
from m_crawler.engine.abstract_response import AbstractResponse as AbstractResponse
from m_crawler.utils.crawler_exception import AllDataCompletedException as AllDataCompletedException
from queue import Queue
from typing import Iterable

class AbstractPipeline(ABC, metaclass=abc.ABCMeta):
    queue: Queue[AbstractRequest | None]
    def __init__(self) -> None: ...
    def proxy_process(self, item: AbstractResponse | AllDataCompletedException) -> None: ...
    @abstractmethod
    def process(self, item: AbstractResponse) -> Iterable[AbstractRequest] | None: ...
