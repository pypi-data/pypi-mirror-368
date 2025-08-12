from m_crawler.engine.abstract_response import AbstractResponse
from m_crawler.engine.abstract_request import AbstractRequest
from typing import Any


class BaseResponse(AbstractResponse):
    def __init__(
        self, request: AbstractRequest, body: Any, success: bool = True
    ) -> None:
        super().__init__(request, body, success)

    def success_handler(self) -> Any:
        return self.body
