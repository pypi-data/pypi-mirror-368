import contextvars
import threading
from abc import ABC, abstractmethod
from contextlib import contextmanager

from m_crawler.engine.abstract_request import AbstractRequest
from m_crawler.engine.abstract_response import AbstractResponse


class AbstractEngine(ABC):
    """
    引擎,提供与网站实际的交互能力
    """

    def __init__(self) -> None:
        self._context = threading.local()

    @staticmethod
    def before_download_hook(request: AbstractRequest) -> AbstractRequest:
        return request

    @staticmethod
    def after_download_hook(result: AbstractResponse) -> AbstractResponse:
        return result

    @abstractmethod
    def download(self, request: AbstractRequest) -> AbstractResponse:
        pass

    @contextmanager
    def context(self):
        yield self._context
        self.after_context()

    def after_context(self):
        self._context = None

    def run(self, request: AbstractRequest) -> AbstractResponse:
        with self.context():
            request = self.before_download_hook(request)
            result = self.download(request)
            result = self.after_download_hook(result)
            return result
