# Deucalion framework

The deucalion framework is a framework for developing Python anomaly detection (AD) applications that are deployed as a sidecar by the deucalion sidecar injector, next to the application exposing prometheus metrics. 

Now it is built to support Prometheus, but extensions can be written to support other monitoring tools as well. 


See the framework's [README.md](deucalionframework/README.md) for information on how to build the framework. 


# Creating a deucalion application

For starters, install the deucalion package. Currently, the deucalion package is hosted on https://test.pypi.org/project/deucalion/, so to install deucalion, run:
```
pip install pip install -i https://test.pypi.org/simple/ deucalion
```

All you need to do to create a deucalion app is described in the following steps: 

### 1. import deucalion
```
import deucalion as dc
```

### 2. Create a subclass of dc.MetricsObserver

Next, create a subclass of the abstract MetricsObserver class and implement the <i>new_data</i> method. This function will be called when new data arrives. 

A simple example of an observer is shown in the code below. It also contains a constructor to provide the AD model object to your observer. 
The new_data method is implemented here to only get a prediction from the model and print the result. 
The return value is None, because of demonstrative purposes. When None is returned, no data is interpreted as anomalous and no alerts are sent to the alertmanager by consenquence. 

```
class SomeAnomalyDetectionMetricsObserver(dc.MetricsObserver):
    def new_data(self, targets_data_dict: Dict[str, Dict[str, Any]]):
        if len(targets_data_dict):
            for target in targets_data_dict:
                pred = self.model.predict(targets_data_dict[target])
                print(target + ': ' + str(targets_data_dict[target]) + ', anomaly score: ' + str(pred))
       
        return None

    def __init__(self, model, desired_metrics: Set[str]):
        super().__init__(desired_metrics)
        self.model = model
```

### 3. Instantiate a MetricsProvisioner and custom MetricsObserver subclass

The last step is to instantiate a MetricsProvisioner. A MetricsProvisioner is responsible for fetching the metrics and providong the data to the registered observers. When instantiating the provider, you specify the desired metrics you want from prometheus. [TODO: still the case? ]
```
myObserver = SomeAnomalyDetectionMetricsObserver(someModel , {
    'go_goroutines',
    'go_gc_heap_allocs_by_size_bytes_total_bucket',
    'node_cpu_seconds_total'
})
provisioner = dc.MetricsProvisioner()
```

Next, register the observer with the provisioner. You can register multiple observers too when multiple models are to be used/tested. The metrics provisioner will only fetch the metrics once and distribute the data over the observers. Registering multiple observers will thus not increase network overhead. The benefit of using mulptiple observers and not manually distributing the data over multple models yourself, is that the new_data methods are invoked in parallel. Every observer gets it's own process to overcome the issue of the Python Global Interpreter Lock (GIL). 
```
provisioner.register(metricsObserver=myObserver)
```


Finally, run the MetricsProvisioner: 
```
provisioner.run()
```
When the provisioner is run, the frameworks takes over control and calls the new_data methods when new data arrives. 
The resulting application looks like this: 

```
from typing import Dict, Any, Set
import deucalion as dc

class SomeAnomalyDetectionMetricsObserver(dc.MetricsObserver):
    def new_data(self, targets_data_dict: Dict[str, Dict[str, Any]]):
        if len(targets_data_dict):
            for target in targets_data_dict:
                pred = self.model.predict(targets_data_dict[target])
                print(target + ': ' + str(targets_data_dict[target]) + ', anomaly score: ' + str(pred))
       
        return None

    def __init__(self, model, desired_metrics: Set[str]):
        super().__init__(desired_metrics)
        self.model = model


if __name__ == '__main__':
    myObserver = SomeAnomalyDetectionMetricsObserver(pm.load(), {
        'go_goroutines',
        'go_gc_heap_allocs_by_size_bytes_total_bucket',
        'node_cpu_seconds_total'
    })
    provisioner = dc.MetricsProvisioner()
    provisioner.register(metricsObserver=myObserver)
    provisioner.run()
```
