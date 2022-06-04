import logging
import os
import time
from multiprocessing import Pool
import yaml
from deucalion.lib.MetricsObserver import MetricsObserver
from deucalion.lib.strategies.PrometheusServerQuerier import PrometheusServerQuerier
from deucalion.lib.strategies.PrometheusTargetScraper import PrometheusTargetScraper
import prom_alertmanager_client as pac
from prom_alertmanager_client.rest import ApiException
from urllib3.exceptions import MaxRetryError
from optparse import OptionParser


class MetricsProvisioner:
    BILLION = 10 ** 9
    STRATEGIES = {}

    def __init__(self):

        # TODO: hier een betere manier voor vinden, want niet alle moeten geinstantieerd worden
        MetricsProvisioner.STRATEGIES['prometheus_sidecar'] = PrometheusTargetScraper
        MetricsProvisioner.STRATEGIES['prometheus_federated'] = PrometheusServerQuerier

        self.logger = logging.getLogger('MetricsProvider')

        self.alert_api_instance = None
        self.api_client = None
        self.strategy = None
        self.currentScrapeInterval = None
        self.INTERVAL_ORIG = None
        self.alert_name = None

        parser = OptionParser()
        parser.add_option("-c", "--config-file", dest="config_filename",
                          help="config file to configure the topology of deucalion", metavar="CONFIG_FILE")
        (options, args) = parser.parse_args()
        config_filename = options.config_filename
        if config_filename is None:
            config_filename = '/etc/deucalion/deucalion_config.yaml'

        self.configure(config_filename)

        # list of observers to notify
        self.observers: [MetricsObserver] = []
        
        # process pool to distribute tasks
        self.processPool = None
        
        # a set of metrics that has to be fetched to provide all obsrver swoth the data they excpect 
        self.desired_metrics = set()
        
    def configure(self, config_filename):
        file_found = False
        while not file_found:
            try:
                with open(config_filename) as config_file:
                    file_found = True
                    config = yaml.safe_load(config_file)

                    self.INTERVAL_ORIG = float(config['metrics_interval'])
                    self.currentScrapeInterval = self.INTERVAL_ORIG
                    config_type = config['type']  # federated of sidecar srtucture
                    if config_type not in MetricsProvisioner.STRATEGIES:
                        raise Exception('Strategy type in configuration file "{}" not registered!'.format(config_type))
                    self.strategy = self.STRATEGIES[config_type]()
                    self.strategy.set_config(config['config'])

                    # AlertManager configuration from environment variables set by the sidecar injector
                    self.alert_name = os.getenv('DEUCALION_ALERT_NAME')
                    alert_manager_host = os.getenv('DEUCALION_ALERT_MANAGER_HOST')
                    alert_manager_port = os.getenv('DEUCALION_ALERT_MANAGER_PORT')
                    if self.alert_name is None or alert_manager_port is None or alert_manager_host is None:
                        self.logger.error('alert manager environment variables not set. Are you injecting this application with the deucalion sidecar injector?')
                        exit(1)
                    alert_config = pac.Configuration()
                    alert_config.host = 'http://' + alert_manager_host + ':' + str(alert_manager_port) + '/api/v2/'
                    self.api_client = pac.ApiClient(alert_config)
                    self.alert_api_instance = pac.AlertApi(self.api_client)
            except FileNotFoundError:
                self.logger.error('Configuration file not found. Did you put the configuration file in the right place?'
                                  + '\t(default /etc/deucalion/deucalion_config.yaml)'
                                  + '\tRetrying in 5 seconds')
                time.sleep(5)

    def register(self, metricsObserver: MetricsObserver):
        self.desired_metrics = self.desired_metrics.union(metricsObserver.desired_metrics)
        self.observers.append(metricsObserver)

    def run(self):  # TODO: new_data roepen per target per metrics of werken met dictionary?
        if len(self.observers) == 0:
            self.logger.error("No observers registered, exiting...")
            exit(1)
        self.logger.info('deucalion metrics provisioner started')

        self.processPool = Pool(len(self.observers))
        execute_time = self.INTERVAL_ORIG * MetricsProvisioner.BILLION + time.time_ns()
        while True:
            metrics = self.strategy.get_metrics(self.desired_metrics)
            if metrics is not None:
                for observer in self.observers:
                    self.logger.info('sending data to observer...')
                    self.processPool.apply_async(observer.new_data, args=(metrics,), callback=self.send_anomaly_alert)
                # self.processPool.join()  # TODO: is joining really necessary? or should you use callback?

            time_delta = execute_time - time.time_ns()
            wait_time_s = time_delta / MetricsProvisioner.BILLION
            if time_delta > 0:
                if wait_time_s > (0.5 * self.currentScrapeInterval) and wait_time_s > self.INTERVAL_ORIG:
                    self.logger.debug("decreasing scrape_interval by 5%")
                    self.currentScrapeInterval *= 0.95
                time.sleep(wait_time_s)

            else:
                self.logger.debug('Scraping interval too low: increasing with 20%')
                self.currentScrapeInterval *= 1.2
            execute_time += self.currentScrapeInterval * MetricsProvisioner.BILLION

    def send_anomaly_alert(self, alert_data):
        if alert_data is not None:
            label_set = {
                "alertname": self.alert_name,
                "alert_data": alert_data
            }
            alert = pac.Alert(label_set)
            try:
                self.alert_api_instance.post_alerts([alert])
            except ApiException as e:
                self.logger.error('Alert manager error: ', e)
            except MaxRetryError:
                self.logger.error('Could not reach Alert Manager. Is the AlertManager running and reachable via the endpoint specified in the configuration file? ')
