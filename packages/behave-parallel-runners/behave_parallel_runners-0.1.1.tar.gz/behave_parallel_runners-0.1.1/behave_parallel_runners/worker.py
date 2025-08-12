from abc import ABC, abstractmethod
from typing import Callable
from threading import Thread

from behave.model import Feature
from behave.configuration import Configuration

from .pool import PoolExecutor


class Worker(ABC):

    _config: Configuration
    _index: int

    def __init__(self, config: Configuration, index: int):
        self._config = config
        self._index = index

    def __str__(self):
        return f"{self.__class__.__name__}-{self.index}"

    def __repr__(self) -> str:
        return "self[%s]" % self.__str__()

    @property
    def index(self) -> int:
        return self._index

    @abstractmethod
    def do(self, work: Callable, feature: Feature) -> None:
        pass

    @abstractmethod
    def done(self) -> bool:
        pass


class ThreadWorker(Worker):

    _thread: None | Thread

    def do(self, work: Callable, feature: Feature) -> None:
        self._thread = Thread(target=work, args=(feature,), name=str(self), daemon=True)
        self._thread.start()

    def done(self) -> bool:
        return not hasattr(self, "_thread") or not self._thread.is_alive()


class WorkerPoolExecutor(PoolExecutor[Worker]):

    def __init__(self, config: Configuration, worker_class: type):
        super().__init__(config, worker_class)

    def done(self) -> bool:
        for worker in self:
            if not worker.done():
                return False
        return True
