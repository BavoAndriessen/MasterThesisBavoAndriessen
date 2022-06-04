from abc import ABC, abstractmethod
from typing import Dict, Any, Set


class MetricsObserver(ABC):
    @abstractmethod
    def new_data(self, data: Dict[str, Dict[str, Any]]):
        raise NotImplementedError

    def __init__(self, desired_metrics: Set[str]):
        self.desired_metrics = desired_metrics