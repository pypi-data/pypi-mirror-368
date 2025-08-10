from abc import ABC, abstractmethod

from m_crawler.engine.abstract_request import AbstractRequest
from m_crawler.engine.abstract_response import AbstractResponse


class AbstractEngine(ABC):
    """
    引擎,提供与网站实际的交互能力
    """

    def before_download_hook(self, request: AbstractRequest) -> AbstractRequest:
        return request

    def after_download_hook(self, result: AbstractResponse) -> AbstractResponse:
        return result

    @abstractmethod
    def download(self, request: AbstractRequest) -> AbstractResponse:
        pass

    def run(self, request: AbstractRequest) -> AbstractResponse:
        request = self.before_download_hook(request)
        result = self.download(request)
        result = self.after_download_hook(result)
        return result
