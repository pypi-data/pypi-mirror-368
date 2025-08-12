from concurrent.futures import Future, ThreadPoolExecutor, as_completed
import threading
from typing import Any, Optional

from loguru import logger
from m_crawler.engine.abstract_engine import AbstractEngine
from m_crawler.engine.abstract_request import AbstractRequest
from m_crawler.engine.abstract_response import AbstractResponse
from m_crawler.pipeline.abstracy_pipeline import AbstractPipeline
from m_crawler.pipeline.json_pipline import JsonPipeline
from m_crawler.scheduler.scheduler import Scheduler
from m_crawler.utils.count_down import CountDown
from m_crawler.utils.crawler_exception import MaxRetryTimeException


class Crawler(threading.Thread):

    lock = threading.Lock()

    def __init__(
        self,
        engine: AbstractEngine,
        pipeline: AbstractPipeline = JsonPipeline(),
        scheduler: Scheduler = Scheduler(),
        threads: int = 1,
        name: str = "Crawler",
        daemon: bool = True,
        max_retry_time: int = 5,
    ) -> None:
        super().__init__(name=name, daemon=daemon)
        self.engine = engine
        self.scheduler = scheduler
        self.pipeline = pipeline
        self.threads = threads
        self.count_down: CountDown = CountDown()
        self.__futures:list[Future] = []
        self.max_retry_time = max_retry_time
        self.__retry_dict = {}

    def append_request(self, *requests: Optional[AbstractRequest]) -> None:
        for request in requests:
            self.scheduler.push(request)

    def run(self) -> None:
        with ThreadPoolExecutor(max_workers=self.threads) as executor:
            for request in self.scheduler.pop():
                if not request:
                    break
                self.count_down.add()
                self.__futures.append(executor.submit(self.__run, request))

        for future in as_completed(self.__futures):
            result = future.result()
            if result:
                logger.info(f"{result} completed")




    def __run(self, request: AbstractRequest) -> Any:
        try:
            response: AbstractResponse = self.engine.run(request)
            if not response.success:
                raise RuntimeError()
            self.pipeline.process(response)
            return request.url
        except Exception as e:
            with Crawler.lock:
                if self.__retry_dict.get(request.url, 0) >= self.max_retry_time:
                    logger.error(e)
                    raise MaxRetryTimeException()
                self.__retry_dict[request.url] = self.__retry_dict.get(request.url, 0) + 1
                logger.warning(f"Retrying {request.url}, Current retry count: {self.__retry_dict[request.url]}")
                self.__run(request)

    def __watch(self, future:Future):
            try:
                result = future.result()
                if result:
                    logger.info(f"{result} completed")
            except Exception as e:
                logger.error(e)
            finally:
                self.count_down.down()
                if self.count_down.count_down() and self.scheduler.queue.empty():
                    self.scheduler.push(None)