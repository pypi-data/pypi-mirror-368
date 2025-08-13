from abc import ABC
from typing import Any, Optional


class AbstractRequest(ABC):
    """
    AbstractRequest
    url: str 请求的 URL
    headers: dict[str, str] 请求头
    params: dict[str, Any] 请求参数
    meta: dict[str, Any] 请求的元数据，通常用于爬虫的数据传递
    """

    __slots__ = ("url", "headers", "params", "meta")

    def __init__(
        self,
        url: str,
        headers: Optional[dict[str, str]] = None,
        params: Optional[dict[str, Any]] = None,
        meta: Optional[dict[str, Any]] = None,
    ) -> None:
        self.url = url
        if headers:
            self.headers = headers
        if params:
            self.params = params
        if meta:
            self.meta = meta
