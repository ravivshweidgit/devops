
Deploying Prometheus using Helm

---

## Instructions

### Deploy Prometheus using Helm Packages

 - Download Helm Client
```
curl -fsSL -o get_helm.sh https://raw.githubusercontent.com/helm/helm/master/scripts/get-helm-3
```

 - Install Helm Client
```
chmod 700 get_helm.sh
./get_helm.sh
```

 -  Add stable helm charts default repository so we we will be able to search and install stable chart from it
 
 ```
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo add stable https://charts.helm.sh/stable
```

-  Update the HELM repositories 
```
helm repo update
```

 - Deploy Prometheus
```
helm install prometheus prometheus-community/prometheus
```

 - List existing pods
```
kubectl get pods
```

 - List existing services
```
kubectl get services
```

 - Please change the type of the prometheus-server service to expose it from outside the cluster
```
kubectl edit svc prometheus-server
```

 - Update the service type
```
kubectl patch svc prometheus-server -p '{"spec": {"type": "LoadBalancer"}}'
```

 - List existing services (wait until the load balancer is created and gets an IP)
```
kubectl get svc --watch
```

 - Browse to prometheus and check the configured targets of the Kubernetes cluster (surprise, everything is already configured!)
```
http://<service-ip>/targets
```

### Cleanup

 - List existing resources
```
kubectl get all
```

 - Delete the installed chart
```
helm delete prometheus
```

 - List existing resources
```
kubectl get all
```
