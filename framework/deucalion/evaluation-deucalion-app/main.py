from typing import Dict, Any, Set
import deucalion as dc
import random


class EvaluationMetricsObserver(dc.MetricsObserver):
    def new_data(self, targets_data_dict: Dict[str, Dict[str, Any]]):
        value = random.random() * 100
        if value < 1:
            return 'anomaly detected'
        return None

    def __init__(self, desired_metrics: Set[str]):
        random.seed()
        super().__init__(desired_metrics)


if __name__ == '__main__':
    myObserver = EvaluationMetricsObserver({
        'istio_requests_total',
        'istio_request_bytes_count'
    })
    provisioner = dc.MetricsProvisioner()
    provisioner.register(metricsObserver=myObserver)
    provisioner.run()