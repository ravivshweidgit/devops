# Kubernetes Workshop
Lab: Kustomize

---

## Instructions

### Install Kustomize

### Clone the repository

 - Clone the example repository
```
git clone .. ~/lab-kustomize
```

### Configure the kustomize deployment

 - Create a directory to store the "base" manifests
```
mkdir ~/lab-kustomize/k8s/base
```

 - Move the base manifests into the "base" directory 
```
mv ~/lab-kustomize/k8s/*.yaml ~/lab-kustomize/k8s/base/
```

 - Create the kustomize.yaml file to group the required manifests
```
cat << EOF >  kustomization.yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

resources:
  - configmap.yaml
  - service.yaml
  - deployment.yaml
EOF
```

 - Deploy the application using Kustomize
```
kubectl apply -k base
```

## Add a common label for all the resources 

- Inspect the resource labels

```
kubectl get deploy the-deployment -o yaml
kubectl get svc demo -o yaml
kubectl get cm the-map -o yaml
```

- Add the following to the Kustomization file in order to add a common label to all the related resources:

```
cat <<EOF >> kustomization.yaml
commonLabels:
  deployment: kustomize
EOF
```

 - Update the application using Kustomize
```
kubectl apply -k base
```

- Inspect the resource labels (note the new label)

```
kubectl get deploy the-deployment -o yaml
kubectl get svc demo -o yaml
kubectl get cm the-map -o yaml
```

## Create configmap and secrets using Kustomize 

 - Create the content for the configmap:

```
cat <<EOF > application.properties
FOO=Bar
EOF
```

 - Create a configmap with the file content by append the content below to the Kustomization file:

```
cat <<EOF >> kustomization.yaml
configMapGenerator:
- name: kustomize-configmap
  files:
  - application.properties
EOF
```

 - Update the application using Kustomize
```
kubectl apply -k base
```

 - Inspect the created configmap (note that kustomize add a unique suffix to the confimap name)
```
kubectl get cm
```

 - Now let's add a secret from the kustomization file (The generated ConfigMaps and Secrets have a content hash suffix appended. This ensures that a new ConfigMap or Secret is generated when the contents are changed. Let's avoid this behavior by using generatorOptions)
```
cat <<EOF >> ~/lab-kustomize/k8s/base/kustomization.yaml
secretGenerator:
- name: kustomize-secret
  literals:
  - username=admin
  - password=secret
generatorOptions:
  disableNameSuffixHash: true
EOF
```

 - Update the application using Kustomize
```
kubectl apply -k ~/lab-kustomize/k8s/base
```

 - Inspect the created secret
```
kubectl get secrets
```

## Use kustomize to add cross-cutting fields

 - Let's append the content below to set cross-cutting fields for all Kubernetes resources in a project:
```
cat <<EOF >> ~/lab-kustomize/k8s/base/kustomization.yaml
namespace: default
namePrefix: prefix-
nameSuffix: "-suffix"
commonAnnotations:
  kustomize: example
EOF
```

 - Update the application using Kustomize
```
kubectl apply -k ~/lab-kustomize/k8s/base
```

## Customize the deployment

 - Let's assume that we have the base deployment ready and we want to create different configurations for our application environments. For that, let's create the overlay folder:
```
mkdir ~/lab-kustomize/k8s/overlays
mkdir ~/lab-kustomize/k8s/overlays/production
mkdir ~/lab-kustomize/k8s/overlays/staging
```

 - The first thing we need to do is create the kustomization file for each environment (which point to the base folder), in addition let's configure it to deploy the resources in a dedicated namespace:
```
cat <<EOF > ~/lab-kustomize/k8s/overlays/staging/kustomization.yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

namespace: staging
bases:
- ../../base
EOF
```
```
cat <<EOF > ~/lab-kustomize/k8s/overlays/production/kustomization.yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

namespace: production
bases:
- ../../base
EOF
```

## Add additional resources

 - Let's add a namespace manifest for each environment:
```
cat <<EOF > ~/lab-kustomize/k8s/overlays/staging/namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: staging
EOF
```
```
cat <<EOF > ~/lab-kustomize/k8s/overlays/production/namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: production
EOF
```

 - Let's add the resource to the kustomization file of each environment:
```
cat <<EOF >> ~/lab-kustomize/k8s/overlays/staging/kustomization.yaml

resources:
- namespace.yaml
EOF
```
```
cat <<EOF >> ~/lab-kustomize/k8s/overlays/production/kustomization.yaml

resources:
- namespace.yaml
EOF
```

## Add/Override configurations

- Now let's update the environment variable for the staging environment, by overriding the configmap:
```
cat <<EOF > ~/lab-kustomize/k8s/overlays/staging/custom-env.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: the-map
data:
  mysqlDB: "mysql.staging.com:3306"
EOF
```

- For production environment, in addition to updating the existing variable, let's create an additional variable:
```
cat <<EOF > ~/lab-kustomize/k8s/overlays/production/custom-env.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: the-map
data:
  mysqlDB: "mysql.production.com:3306"
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: the-deployment
spec:
  template:
    spec:
      containers:
        - name: the-container
          env:
            - name: NEW_VARIABLE
              value: "my-variable"
EOF
```

- Add the configurations above to the kustomization file of each environment:
```
cat <<EOF >> ~/lab-kustomize/k8s/overlays/staging/kustomization.yaml

patchesStrategicMerge:
- custom-env.yaml
EOF
```
```
cat <<EOF >> ~/lab-kustomize/k8s/overlays/production/kustomization.yaml

patchesStrategicMerge:
- custom-env.yaml
EOF
```

- Deploy the resources of each environment:

```
kubectl apply -k ~/lab-kustomize/k8s/overlays/staging
kubectl apply -k ~/lab-kustomize/k8s/overlays/production
```

- Inspect the created resources:

```
kubectl describe cm prefix-the-map-suffix -n staging
kubectl describe cm prefix-the-map-suffix -n production
kubectl get deploy -n production
```


### Cleanup

 - List existent resources
```
kubectl get all
```

 - Delete existent resources
```
kubectl delete all --all
kubectl delete all --all -n staging
kubectl delete all --all -n production
kubectl delete namespace staging production
```

 - List existent resources
```
kubectl get all
```
