# Generating TLS secrets for the MutatingAdmissionWebhook service

The cfssl tool is used to generate the CA and TLS certificate and key. 
See the cfssl repo for more information about the cfssl tool: https://github.com/cloudflare/cfssl

# Step 1: Generate CA
First generate a CA. If you already have a CA that you want to use, go to the next step. 

Use the ```ca-csr.json``` as the configuration file or modify it to fit your needs. 
```
cfssl gencert -initca ca-csr.json | cfssljson -bare ca
```

# Step 2: Generate certificate
Generate your certificate, using the generated CA or your own CA. Note that the hostname parameter is important: it should be in accordance with how the webhook service is eventually deployed (service name and namspace). Modify this parameter value when other values are used when installing the control plane. 
```
cfssl gencert \
    -ca=ca.pem \
    -ca-key=ca-key.pem \
    -config=ca-config.json \
    -hostname="deucalion-sidecar-injector-service.deucalion-system.svc.cluster.local,deucalion-sidecar-injector-service,deucalion-sidecar-injector-service.deucalion-system.svc,localhost,127.0.0.1" \
    -profile=default \
    ca-csr.json | cfssljson -bare webhook-tls
```

<!-- # Step 3: Add webhook-tls.pem and webhook-tls-key.pem to kubernetes as a Secret
(this step is only required when installing manually, without helm)

Add the contents of the generated files to a k8s Secret, base64 encoded. Store these Secrets in Kubernetes. 
```
apiVersion: v1
kind: Secret
metadata:
  name: "deucalion-sidecar-injector-tls"
type: kubernetes.io/tls
data:
  tls.cert: |
    <base64 encoded webhook-tls.pem>
  tls.key: |
    <base64 encoded webhook-tls-key.pem>
```


# Step 4: Add CA bundle to webhook configuration (webhook.yml)
(this step is only required when installing manually, without helm)

Now, the CA bundle must be added to the MutatingWebhookConfiguration. 
```
openssl base64 -A < "ca.pem"
```

Add the output of this command to webhook.yaml file at the "caBundle" key of the MutatingWebhookConfiguration.  -->