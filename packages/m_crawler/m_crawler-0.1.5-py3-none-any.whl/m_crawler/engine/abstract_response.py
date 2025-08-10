from abc import ABC, abstractmethod
from typing import Any
from loguru import logger

from m_crawler.engine.abstract_request import AbstractRequest


class AbstractResponse(ABC):
    def __init__(
        self, request: AbstractRequest, body: Any, success: bool = True
    ) -> None:
        self.request = request
        self.body = body
        self.success = success

    @abstractmethod
    def success_handler(self) -> Any:
        pass

    def fail_handler(self, exception: Exception) -> None:
        logger.error(f"{self.request.url} fetch error, {exception}")

    def handle(self) -> Any:
        try:
            return self.success_handler()
        except Exception as e:
            self.fail_handler(e)
