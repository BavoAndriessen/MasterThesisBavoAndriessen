import abc
from typing import Dict, Set, Any


class MetricsFetcherStrategy(abc.ABC):
    @abc.abstractmethod
    def get_metrics(self, desired_metrics: Set[str]) -> Dict[str, Any]:
        raise NotImplementedError

    @abc.abstractmethod
    def set_config(self, config):
        raise NotImplementedError
