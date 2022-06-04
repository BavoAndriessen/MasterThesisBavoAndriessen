see the cfssl repo for more information about the cfssl tool: https://github.com/cloudflare/cfssl

# Step 1: Generate CA
First generate a CA. If you already have a CA that you want to use, go to the next step. 
```

cfssl gencert -initca ca-csr.json | cfssljson -bare ca

```

# Step 2: Generate certificate
Generate your certificate, using the generated or your own CA. Note that the hostname parameter is important: it should be in accordance with how the webhook service is eventually deployed (service name and namspace). Modify this parameter value when other values are used. 
```
cfssl gencert \
    -ca=ca.pem \
    -ca-key=ca-key.pem \
    -config=ca-config.json \
    -hostname="deucalion-sidecar-injector-service.deucalion-system.svc.cluster.local,deucalion-sidecar-injector-service,deucalion-sidecar-injector-service.deucalion-system.svc,localhost,127.0.0.1" \
    -profile=default \
    ca-csr.json | cfssljson -bare webhook-tls

```

# Step 3: Add webhook-tls.pem and webhook-tls-key.pem to kubernetes as a Secret

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
using this command: 
```
openssl base64 -A < "ca.pem"
```

Add the output of this command to webhook.yaml file at the "caBundle" key. 