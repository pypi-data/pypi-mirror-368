import abc
from _typeshed import Incomplete
from abc import ABC, abstractmethod
from m_crawler.engine.abstract_request import AbstractRequest as AbstractRequest
from typing import Any

class AbstractResponse(ABC, metaclass=abc.ABCMeta):
    request: Incomplete
    body: Incomplete
    success: Incomplete
    def __init__(self, request: AbstractRequest, body: Any, success: bool = True) -> None: ...
    @abstractmethod
    def success_handler(self) -> Any: ...
    def fail_handler(self, exception: Exception) -> None: ...
    def handle(self) -> Any: ...
