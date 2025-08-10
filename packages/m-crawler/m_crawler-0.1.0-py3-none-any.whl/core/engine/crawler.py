from concurrent.futures import Future, ThreadPoolExecutor, as_completed
import threading
from typing import Any, Callable, Optional, Sequence

from loguru import logger
from core.engine.abstract_engine import AbstractEngine
from core.engine.abstract_request import AbstractRequest
from core.engine.abstract_response import AbstractResponse
from core.pipeline.abstracy_pipeline import AbstractPipeline
from core.pipeline.json_pipline import JsonPipeline
from core.scheduler.scheduler import Scheduler
from core.utils.count_down import CountDown
from core.utils.crawler_exception import MaxRetryTimeException


class Crawler:

    lock = threading.Lock()

    def __init__(
        self,
        engine: AbstractEngine,
        pipeline: AbstractPipeline = JsonPipeline(),
        scheduler: Scheduler = Scheduler(),
        parsers: Sequence[Callable[[AbstractResponse], Any]] = [],
        threads: int = 1,
    ) -> None:
        self.engine = engine
        self.scheduler = scheduler
        self.pipeline = pipeline
        self.parsers = parsers
        self.threads = threads
        self.count_down: CountDown = CountDown()

    def append_request(self, *requests: Optional[AbstractRequest]) -> None:
        for request in requests:
            self.scheduler.push(request)

    def start(self) -> None:
        futures: list[Future[None]] = []
        with ThreadPoolExecutor(max_workers=self.threads) as executor:
            while True:
                request = self.scheduler.pop()
                if not request:
                    if self.scheduler.no_more_data:
                        break
                    else:
                        continue
                self.count_down.add()
                futures.append(executor.submit(self.__run, request))

        for future in as_completed(futures):
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

    def __run(self, request: AbstractRequest) -> Any:

        try:
            response: AbstractResponse = self.engine.run(request)
            self.pipeline.process(response)
            return request.url
        except Exception as e:
            retriable = self.scheduler.push_retry(request)
            if not retriable:
                logger.error(e)
                raise MaxRetryTimeException()
            return None
