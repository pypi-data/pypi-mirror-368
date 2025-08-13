from concurrent.futures import Future, ThreadPoolExecutor, as_completed
import threading
from loguru import logger

from m_crawler.engine.abstract_engine import AbstractEngine
from m_crawler.engine.abstract_request import AbstractRequest
from m_crawler.engine.abstract_response import AbstractResponse
from m_crawler.pipeline.abstracy_pipeline import AbstractPipeline
from m_crawler.utils.crawler_exception import MaxRetryTimeException


class Crawler(threading.Thread):

    lock = threading.Lock()

    def __init__(
        self,
        engine: AbstractEngine,
        input_pipeline: AbstractPipeline,
        output_pipeline: AbstractPipeline,
        threads: int = 1,
        name: str = "Crawler",
        daemon: bool = True,
        max_retry_time: int = 5,
    ) -> None:
        super().__init__(name=name, daemon=daemon)
        self.engine = engine
        self.input_pipeline = input_pipeline
        self.output_pipeline = output_pipeline
        self.threads = threads
        self.max_retry_time = max_retry_time
        self.__retry_dict: dict[str, int] = {}

    def run(self) -> None:
        futures: list[Future[None]] = []
        with ThreadPoolExecutor(max_workers=self.threads) as executor:
            while True:
              resuest = self.input_pipeline.queue.get(block=True)
              if resuest is None:
                break
              futures.append(executor.submit(self.__run, resuest))

        for future in as_completed(futures):
            future.result()
              
    
    def __run(self, request: AbstractRequest) -> None:
        response:AbstractResponse = None # type: ignore
        try:
            response = self.engine.run(request)
            if not response.success:
                raise RuntimeError()
        except Exception:
                with Crawler.lock:
                    logger.error(f"Retrying {request.url}")
                    self.__retry_dict[request.url] = self.__retry_dict.get(request.url, 0) + 1
                    if self.__retry_dict[request.url] > self.max_retry_time:
                        logger.error(f"Max retry time reached for {request.url}")
                        raise MaxRetryTimeException()
                    logger.warning(f"Retrying {request.url}, Current retry count: {self.__retry_dict[request.url]}")
                    self.__run(request)
        self.output_pipeline.process(response)

