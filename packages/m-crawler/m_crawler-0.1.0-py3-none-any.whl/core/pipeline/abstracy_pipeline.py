from abc import ABC, abstractmethod
from typing import Any, Optional, Set

from core.scheduler.scheduler import Scheduler


class AbstractPipeline(ABC):

    def __init__(self) -> None:
        self.schedulers: Optional[Set[Scheduler]] = None

    def register_scheduler(self, scheduler: Scheduler) -> None:
        if self.schedulers is None:
            self.schedulers = set()
        self.schedulers.add(scheduler)

    def process(self, item: Any) -> None:
        process_result = self.process_item(item)
        if self.schedulers:
            for scheduler in self.schedulers:
                scheduler.push(process_result)

    @abstractmethod
    def process_item(self, item: Any) -> Any:
        """
        处理 engine 获取的数据
        """
        pass
