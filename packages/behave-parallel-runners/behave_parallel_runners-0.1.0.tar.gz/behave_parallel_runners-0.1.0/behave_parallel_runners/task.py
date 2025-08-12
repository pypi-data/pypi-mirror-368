from abc import ABC, abstractmethod
from collections import deque

from behave.model import Feature
from behave.configuration import Configuration
from behave.runner_util import parse_features, collect_feature_locations


class FeatureFinder:
    _config: Configuration

    def __init__(self, config: Configuration):
        self._config = config

    def _find_feature_location(self) -> list[str]:
        return [
            filename
            for filename in collect_feature_locations(self._config.paths)
            if not self._config.exclude(filename)
        ]

    def get_all_features(self) -> list[Feature]:
        return parse_features(self._find_feature_location(), language=self._config.lang)


class TaskAllocator(ABC):

    _config: Configuration
    _feature_finder: FeatureFinder

    def __init__(self, config: Configuration):
        self._config = config
        self._feature_finder = FeatureFinder(config)

    @abstractmethod
    def allocate(self, job_number: int) -> Feature:
        pass

    @abstractmethod
    def empty(self) -> bool:
        pass


class FeatureTaskAllocator(TaskAllocator):

    _features: deque[Feature]

    def __init__(self, config: Configuration):
        super().__init__(config)
        self._features = deque(self._feature_finder.get_all_features())

    def allocate(self, _: int) -> Feature:
        if self.empty():
            raise IndexError("No more features to allocate")
        return self._features.popleft()

    def empty(self) -> bool:
        return len(self._features) == 0
