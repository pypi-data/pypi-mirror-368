from _typeshed import Incomplete
from m_crawler.engine.abstract_engine import AbstractEngine as AbstractEngine
from m_crawler.engine.abstract_request import AbstractRequest as AbstractRequest
from m_crawler.engine.abstract_response import AbstractResponse as AbstractResponse
from m_crawler.pipeline.abstracy_pipeline import AbstractPipeline as AbstractPipeline
from m_crawler.pipeline.json_pipline import JsonPipeline as JsonPipeline
from m_crawler.scheduler.scheduler import Scheduler as Scheduler
from m_crawler.utils.count_down import CountDown as CountDown
from m_crawler.utils.crawler_exception import MaxRetryTimeException as MaxRetryTimeException
from typing import Any, Callable, Sequence

class Crawler:
    lock: Incomplete
    engine: Incomplete
    scheduler: Incomplete
    pipeline: Incomplete
    parsers: Incomplete
    threads: Incomplete
    count_down: CountDown
    def __init__(self, engine: AbstractEngine, pipeline: AbstractPipeline = ..., scheduler: Scheduler = ..., parsers: Sequence[Callable[[AbstractResponse], Any]] = [], threads: int = 1) -> None: ...
    def append_request(self, *requests: AbstractRequest | None) -> None: ...
    def start(self) -> None: ...
