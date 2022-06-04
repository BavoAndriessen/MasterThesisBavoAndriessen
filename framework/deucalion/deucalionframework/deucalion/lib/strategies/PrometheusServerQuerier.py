import json
import logging
from typing import Dict, Set, Any
import requests
from deucalion.lib.strategies.MetricsFetcherStrategy import MetricsFetcherStrategy


class PrometheusServerQuerier(MetricsFetcherStrategy):
    def __init__(self):
        self.logger = logging.getLogger('PrometheusTargetQuerier')
        self.targets = []
        self.server_port = None

    def get_metrics(self, desired_metrics: Set[str]) -> Dict[str, Any]:
        self.targets = []
        res = {}
        try:
            # query targets from prometheus server
            r_json = requests.get('http://localhost:{}/api/v1/targets'.format(self.server_port)).json()
            for target_object in r_json['data']['activeTargets']:
                self.targets.append(target_object['discoveredLabels']['__address__'])

            for target in self.targets:
                target_data = self.query_metrics(desired_metrics, target)
                res[target] = target_data

        except requests.exceptions.ConnectionError:
            self.logger.error("Could not get targets from server")

        return res

    def set_config(self, config):
        self.server_port = config['server_port']

    def query_metrics(self, desired_metrics: [str], target: str): ## TODO: uitbreiden om meerdere targets in een keer te querien door matching string
        metrics_query_str = '|'.join(desired_metrics)  # get all desired metrics in one request using the OR operator, select deired labels later
        metrics = requests.get('http://localhost:' + str(self.server_port) + '/api/v1/query?query={__name__=~"' + metrics_query_str + '", instance="' + target + '"}').json()['data']['result']
        res = {}
        for metric in metrics:
            if metric['metric']['__name__'] not in res:
                res[metric['metric']['__name__']] = {}
            labels_object = {}
            for label in metric['metric']:
                if label != '__name__' and label != 'job' and label and label != 'instance':
                    labels_object[label] = metric['metric'][label]
                    # if label not in res[metric['metric']['__name__']]:
                    #     res[metric['metric']['__name__']][label] = {}
                    # res[metric['metric']['__name__']][label][metric['metric'][label]] = metric['value'][1]  # first element is timestamp, second is value
            labels_string = json.dumps(labels_object)
            res[metric['metric']['__name__']][labels_string] = metric['value'][1]
        return res
