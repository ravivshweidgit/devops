
## Instructions


 - Create a new namespace for the ingress controller
```
kubectl create namespace ingress-nginx
```

 - Deploy the required resources of the Ingress controller:
```
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.2.1/deploy/static/provider/cloud/deploy.yaml
```

 - Verify NGINX controller installation 
```
kubectl get pods -n ingress-nginx -l app.kubernetes.io/name=ingress-nginx --watch
```

 - Inspect the ingress controller Service
```
kubectl get svc ingress-nginx-controller -n ingress-nginx
```

### Deploy the application


 - Deploy the "**Cats**" application
```
kubectl create -f cats.yaml
```

 - Deploy the "**Dogs**" application

```
kubectl create -f dogs.yaml
```


 - Deploy the "**Birds**" application
```
kubectl create -f birds.yaml
```


 - Create the ingress resource
```
kubectl create -f ingress.yaml
```

 - List existing pods
```
kubectl get pods
```

 - List existing services
```
kubectl get svc
```

 - List existing ingress 
```
kubectl get ingress
```

### Access the application

 - Get the ingress controller External IP 
```
kubectl get svc ingress-nginx-controller -n ingress-nginx
```
In minikube 
```
minikube service ingress-nginx-controller --url -n ingress-nginx
```
In minikube Use the URL that you get (like: http://127.0.0.1:62512 ) 

ingress-controller-external-ip or minikube URL

 - Browse to the cats service
```
http://<ingress-controller-external-ip>/cats
```

 - Browse to the dogs service
```
http://<ingress-controller-external-ip>/dogs
```

 - Browse to the birds service
```
http://<ingress-controller-external-ip>/birds
```

### Cleanup

 - List existing resources
```
kubectl get all
```

 - Delete ingress resource
```
kubectl delete ingress --all
```

 - Delete existing resources
```
kubectl delete all --all
kubectl delete all --all -n ingress-nginx
kubectl delete namespace ingress-nginx
```

 - List existing resources
```
kubectl get all
```
