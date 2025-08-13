import threading
from _typeshed import Incomplete
from m_crawler.engine.abstract_engine import AbstractEngine as AbstractEngine
from m_crawler.engine.abstract_request import AbstractRequest as AbstractRequest
from m_crawler.engine.abstract_response import AbstractResponse as AbstractResponse
from m_crawler.pipeline.abstracy_pipeline import AbstractPipeline as AbstractPipeline
from m_crawler.utils.crawler_exception import AllDataCompletedException as AllDataCompletedException, MaxRetryTimeException as MaxRetryTimeException

class Crawler(threading.Thread):
    lock: Incomplete
    engine: Incomplete
    input_pipeline: Incomplete
    output_pipeline: Incomplete
    threads: Incomplete
    max_retry_time: Incomplete
    def __init__(self, engine: AbstractEngine, input_pipeline: AbstractPipeline, output_pipeline: AbstractPipeline, threads: int = 1, name: str = 'Crawler', daemon: bool = True, max_retry_time: int = 5) -> None: ...
    def run(self) -> None: ...
