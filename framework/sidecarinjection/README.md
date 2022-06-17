# Sidecar injector

## Prerequisites: 
go version 1.17

## Build
```
go build deucalion-sidecar-injector.go
```

## running

To run the sidecar injector, two commands can be used: ```manual``` and ```webhook```. Only the ```webhook``` command functions. 

```
./deucalion-sidecar-injector <command> <flags...>
```

The ```webhook``` command should be used for the automatic sidecar injector. Some command line flags are expected. To see which, take a look at the example use in the ```args``` section in [the sidecar injector service deployment manifest](../deploy/helm/deucalion-sidecar-injection-chart/templates/MutatingAdmissionControllerWebhook.yaml) from the helm chart, or check out [webhook.go](./webhook/webhook.go) for available flags and their behaviour. 

