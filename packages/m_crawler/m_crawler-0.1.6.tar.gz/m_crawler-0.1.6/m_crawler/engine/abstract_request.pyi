from _typeshed import Incomplete
from abc import ABC
from typing import Any

class AbstractRequest(ABC):
    url: Incomplete
    headers: Incomplete
    params: Incomplete
    meta: Incomplete
    def __init__(self, url: str, headers: dict[str, str] | None = None, params: dict[str, Any] | None = None, meta: dict[str, Any] | None = None) -> None: ...
