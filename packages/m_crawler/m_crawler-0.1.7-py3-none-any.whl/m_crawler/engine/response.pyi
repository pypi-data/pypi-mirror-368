from m_crawler.engine.abstract_request import AbstractRequest as AbstractRequest
from m_crawler.engine.abstract_response import AbstractResponse as AbstractResponse
from typing import Any

class BaseResponse(AbstractResponse):
    def __init__(self, request: AbstractRequest, body: Any, success: bool = True) -> None: ...
    def success_handler(self) -> Any: ...
