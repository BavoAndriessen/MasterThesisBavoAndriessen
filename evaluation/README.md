# Evaluation

## Test Setups
The evaluation was performed on 4 deployment setups, all on top of Istio: 

1. Without monitoring
    
    In this setup, the Bookinfo application is deployed normally, without any kind of monitoring. 
    The application was deployed using [this kubernetes manifest](./bookinfo.yaml). 

2. Standard Prometheus monitoring

    In this setup, Prometheus is enabled for monitoring the Istio proxies. 
    The Bookinfo application was deployed using [this kubernetes manifest](./bookinfo.yaml) and Prometheus was deployed with [this manifest](./standard_prometheus.yaml).


3. Proposed framework - sidecar architecture
    
    Here, Prometheus is not installed on the cluster, because the framework is used for monitoring and anomaly detection. 
    The same [Kubernetes manifest](./bookinfo.yaml) can be used to deploy the application. 
    The control plane components need to be installed on the cluster using the provided helm chart. Installation instructions can be found in this [README.md](../framework/deploy/README.md).


4. Proposed framework - federated architecture
    
    In this setup, the application is monitored by the framework in federated mode. 
    The control plane must be redeployed. The for this is because the service account must be installed in the right namespace to be accessible. To uninstall the components, use ```helm uninstall <release_name>```. Modify the ```applicationNamespace``` field in [values.yaml](./../framework/deploy/helm/deucalion-sidecar-injection-chart/values.yaml) to specify the namespace in which the deucalion sidecars will be deployed. The value should be the namespace of the prometheus servers. After configured correctly, use the provided ```helm install``` command in the deployment [README.md](../framework/deploy/README.md). 

    Also, reconfigure the Configmap containing the configuration for the sidecars. To avoid conflicts with the previous deployment (with sidecar architecture), delete all application specific resources ([bookinfo.yaml](./bookinfo.yaml)) and apply [this manifest](./bookinfo_federated.yaml) instead. This manifests configures the services to belong to a certain federation. 

    To deploy the federated prometheus servers, apply [this manifest](./federated-prometheus.yaml). This configuration of ensures that different prometheus server are set up to only scrape the targets of a specific federation. 

    
## Data 

The data was gathered by cAdvisor instances. cAdvisor provides instructions on how to install it [here](https://github.com/google/cadvisor/tree/master/deploy/kubernetes). One modification was made in the daemonset.yaml file. The monified version is provided in this [daemonset.yaml](./daemonset.yaml) file. The monifications include arguments to specify the influxDB service to which the data is sent. 

To install influxDB, the [instructions from InfluxData](https://github.com/influxdata/helm-charts) were followed. Note that a persistent volume must be available for use by influxdb. For this avaluation, [pv.yaml](./pv.yaml) was used to create a PersistentVolume which is simply a hostPath, but in principle, any kind could be used. Only InfluxDB and Chronograph were installed. Chronograph is not really necessary, but it was used to inspect the data and download the data. 

The data from cAdvisor could also be collected by a Prometheus server, but consider that the default Prometheus server should then be adapted in order to avoid that the server also scraping the Istio proxies, which will influence the measurements of the evaluation. 

The collected data can be found in the ```data``` directory. It was manually downloaded from the Chronograph web interface. 


## Data analysis

Please read the [notebook](./evaluation.ipynb), in which the data analysis is performed and explained. 


## Load tests to evaluate scalability

To evaluate the scalability of applications being monitored by Deucalion, Locust load tests were performed to determine teh sturation point of the applications in all test setups. [locustfile.py](./locustfile.py) was used. It is not at all complex, because the application itself (Bookinfo) is not complex either.

The data analysis of these tests can also be found in the notebook. 