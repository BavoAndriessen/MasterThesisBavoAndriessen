import json
import logging
import socket
from typing import Dict, Set, Any
from prometheus_client.parser import text_string_to_metric_families
import requests
from deucalion.lib.strategies.MetricsFetcherStrategy import MetricsFetcherStrategy
from kubernetes import client, config


class PrometheusTargetScraper(MetricsFetcherStrategy):
    def __init__(self):
        self.namespace = None
        self.logger = logging.getLogger('PrometheusTargetScraper')
        self.metrics_path = None
        self.targets: [str] = None
        self.v1client = None

        try:
            config.load_incluster_config()
            self.v1client = client.CoreV1Api()
        except config.config_exception.ConfigException:
            self.logger.error(
                'Could not access service account token file. Are you running this application in a kubernetes cluster?')
            exit(1)

    def get_targets_from_kube_api(self):
        pod_annotations = self.v1client.read_namespaced_pod(socket.gethostname(), self.namespace).metadata.annotations
        if not pod_annotations.get('prometheus.io/scrape'):
            # TODO: exiten, normaal moet de injector die er uit selecteren wel
            pass
        self.metrics_path = pod_annotations.get('prometheus.io/path')
        self.targets = []
        self.targets.append('localhost:' + pod_annotations.get('prometheus.io/port'))
        self.logger.info('targets:', self.targets)

    def get_metrics(self, desired_metrics: Set[str]) -> Dict[str, Any]:
        res = {}
        for target in self.targets:
            try:
                res_dict = {}
                r = requests.get('http://' + target + '/' + self.metrics_path)  # TODO: https ondersteuning
                for family in text_string_to_metric_families(r.text):
                    for sample in family.samples:
                        metric_name = sample[0]  # sample[0] is metric name
                        if metric_name in desired_metrics:
                            labels_string = json.dumps(sample[1])
                            if metric_name not in res_dict:
                                res_dict[metric_name] = {}
                            res_dict[metric_name][labels_string] = sample[2]  # value
                    res[target] = res_dict
            except requests.exceptions.ConnectionError:
                self.logger.error('Could not get metrics from target {}'.format(target))

        return res

    def set_config(self, config_object):
        self.namespace = config_object['namespace']
        self.get_targets_from_kube_api()
