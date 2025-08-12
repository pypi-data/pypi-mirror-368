import threading
from _typeshed import Incomplete
from m_crawler.engine.abstract_engine import AbstractEngine as AbstractEngine
from m_crawler.engine.abstract_request import AbstractRequest as AbstractRequest
from m_crawler.engine.abstract_response import AbstractResponse as AbstractResponse
from m_crawler.pipeline.abstracy_pipeline import AbstractPipeline as AbstractPipeline
from m_crawler.pipeline.json_pipline import JsonPipeline as JsonPipeline
from m_crawler.scheduler.scheduler import Scheduler as Scheduler
from m_crawler.utils.count_down import CountDown as CountDown
from m_crawler.utils.crawler_exception import MaxRetryTimeException as MaxRetryTimeException

class Crawler(threading.Thread):
    lock: Incomplete
    engine: Incomplete
    scheduler: Incomplete
    pipeline: Incomplete
    threads: Incomplete
    count_down: CountDown
    def __init__(self, engine: AbstractEngine, pipeline: AbstractPipeline = ..., scheduler: Scheduler = ..., threads: int = 1) -> None: 
        self.__futures = None
        self.__run = None
        ...
    def append_request(self, *requests: AbstractRequest | None) -> None: ...
    def run(self) -> None: ...

    def __watch(self):
        pass
