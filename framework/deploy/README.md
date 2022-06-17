# Deploying an application with the Deucalion framework 

## 1. Create an anomaly detection app using the Python framework 
If you don't already have a Deucalion application available (the image bavoandriessen/deucalion-app:latest dummy application is available on DockerHub), follow the instructions in the [README.md file](../deucalion/README.md) of the deucalion framework to create a deuclaion sidecar application. 

When created, containerize your AD application: 
- An example development Dockerfile can be found [here](../deucalion/Dockerfile). 
- An example production Dockerfile can be found [here](../deucalion/example_app/Dockerfile)

## 2. Deploying the control plane components of the control plane with Helm

Installing the control plane is a tedious task, therefore, a Helm chart is provided. 


### values.yaml
Some values in [values.yaml](./helm/deucalion-sidecar-injection-chart/values.yaml) need to be set, depending on your future application deployments. 

These values should probabliy be verified before installing: 

- ```admissionController.webhookService.args.defaultSidecarImage```: the image of the default sidecar image. If no image is specified in a deployment, this image will be used. 
- ```admissionController.webhookService.image```: the image of the sidecarinjector. 
- ```applicationNamespace```: this is the namespace in which the deucalion sidecars will be injected. The serviceaccount used by the sidecars must be deployed in the same namespace as the sidecar itself. In the case of the sidecar architecture, specify the namespace in which the applications will be deployed, in the case of the federated apporach, specify the namespace in which the federated prometheus servers will be deployed. 

### TLS
To automatically inject sidecars into pods, a MutatingAdmissionWebhoook Controller is configured. The k8s api server then sends admission reviews to this webhook, which it will only do over TLS, so you will have to manually create a TLS certificate, signed by a CA. 

Follow steps 1 and 2 in this [README.md](../sidecarinjection/configuration/tls/README.md) to generate the TLS certificate and CA bundle. 

When installing with Helm, some values must be set to fill in the generated TLS values (base64 encoded) into the chart. This can be done with the following example command: 
```
helm upgrade --install deucalion-sidecar-injection-chart-1649709429 deucalion-sidecar-injection-chart --set admissionController.webhookService.caBundle="$(base64 <path to ca.pem>)" --set admissionController.webhookService.tlsCrt="$(base64 <path to webhook-tls.pem>)" --set admissionController.webhookService.tlsKey="$(base64 <path to webhook-tls-key.pem>)"
```



## 3. Deploy your application

An example deployment can be found [here](./example-deployment/nodeexporter-deployment.yml). 

### Configuration
Before deploying your application, a ConfigMap needs to be created that contains configuration for the sidecars. 

The configuration file contains the scrape interval and architecture specific configuration. In the case of the sidecar architecture, the namespace must be specified (exmaple [here](./example-deployment/nodeexporter-deployment.yml)). In the case of the federated approach, the port of the adjecent prometheus server must be specified (example in [bookinfo_federated.yaml](../../evaluation/bookinfo_federated.yaml) used in the evaluation). 


### Annotate PodSpec

Add Prometheus annotations (```prometheus.io/path```, ```prometheus.io/port```, ```prometheus.io/scrape```) as you would normally do when monitored by Prometheus. 

Annotate the Pods with the necessary deucalion specific annotations: 
- deucalion-sidecar-image: <deucalion_sidecar_image>
- deucalion-config-map: <deucalion-sidecar-config-map>

### Deploy

Apply the modified templates/manifests to k8s and the sidecars should be automatically injected and they should be monitoring your application and sending anomaly alerts to the alertmanager when alerts are detected. 
