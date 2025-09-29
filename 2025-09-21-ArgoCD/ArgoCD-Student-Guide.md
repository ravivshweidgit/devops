# ArgoCD Student Guide

## Table of Contents
1. [Introduction](#introduction)
2. [Prerequisites](#prerequisites)
3. [Environment Setup](#environment-setup)
4. [ArgoCD Installation](#argocd-installation)
5. [Accessing ArgoCD UI](#accessing-argocd-ui)
6. [Creating Applications via UI](#creating-applications-via-ui)
7. [ArgoCD CLI](#argocd-cli)
8. [Application Management](#application-management)
9. [Homework Assignment](#homework-assignment)
10. [Summary](#summary)

## Introduction

ArgoCD is a declarative, GitOps continuous delivery tool for Kubernetes. It automates the deployment of applications to Kubernetes clusters by monitoring Git repositories and ensuring that the live state matches the desired state defined in Git.

### Key Features:
- **GitOps**: Uses Git as the single source of truth
- **Declarative**: Describes the desired state of applications
- **Automated**: Continuously monitors and syncs applications
- **Multi-cluster**: Can manage multiple Kubernetes clusters
- **Web UI**: User-friendly interface for application management
- **CLI**: Command-line interface for automation

## Prerequisites

Before starting this lesson, ensure you have:
- Basic understanding of Kubernetes concepts
- `kubectl` installed and configured
- `minikube` installed (for local development)
- Basic knowledge of Git and YAML

## Environment Setup

### 1. Start Minikube

```bash
minikube start
```

This command starts a local Kubernetes cluster using Minikube, which will serve as our target cluster for ArgoCD deployments.

## ArgoCD Installation

### 1. Create ArgoCD Namespace

```bash
kubectl create ns argocd
```

**Output:**
```
namespace/argocd created
```

**Explanation:** We create a dedicated namespace called `argocd` to isolate ArgoCD components from other applications in the cluster.

### 2. Install ArgoCD

```bash
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
```

**Explanation:** This command downloads and applies the official ArgoCD installation manifest. It creates all necessary Kubernetes resources including:
- Deployments
- Services
- ConfigMaps
- Secrets
- RBAC resources

### 3. Verify Installation

Check that all ArgoCD pods are running:

```bash
kubectl get po -n argocd
```

**Expected Output:**
```
NAME                                                READY   STATUS    RESTARTS      AGE
argocd-application-controller-0                     1/1     Running   0             73s
argocd-applicationset-controller-54f96997f8-g8bsn   1/1     Running   0             74s
argocd-dex-server-798cbff4c7-ngp9n                  1/1     Running   1 (37s ago)   74s
argocd-notifications-controller-644f66f7df-hlg6z    1/1     Running   0             74s
argocd-redis-6684c6947f-gj4lc                       1/1     Running   0             74s
argocd-repo-server-6fccc5759b-zhgrg                 1/1     Running   0             74s
argocd-server-64d5fcbd58-4l5lh                      1/1     Running   0             74s
```

**Component Explanation:**
- **application-controller**: Core component that monitors applications and syncs them
- **applicationset-controller**: Manages ApplicationSets for bulk application management
- **dex-server**: Handles authentication and authorization
- **notifications-controller**: Manages notifications and webhooks
- **redis**: In-memory data store for caching
- **repo-server**: Fetches and caches Git repository contents
- **server**: Web UI and API server

### 4. Check Services

```bash
kubectl get svc -n argocd
```

**Expected Output:**
```
NAME                                      TYPE        CLUSTER-IP       EXTERNAL-IP   PORT(S)                      AGE
argocd-applicationset-controller          ClusterIP   10.103.55.225    <none>        7000/TCP,8080/TCP            2m22s
argocd-dex-server                         ClusterIP   10.102.64.189    <none>        5556/TCP,5557/TCP,5558/TCP   2m22s
argocd-metrics                            ClusterIP   10.110.212.115   <none>        8082/TCP                     2m22s
argocd-notifications-controller-metrics   ClusterIP   10.99.48.57      <none>        9001/TCP                     9m15s
argocd-redis                              ClusterIP   10.98.195.235    <none>        6379/TCP                     2m22s
argocd-repo-server                        ClusterIP   10.107.188.129   <none>        8081/TCP,8084/TCP            2m22s
argocd-server                             ClusterIP   10.110.13.100    <none>        80/TCP,443/TCP               2m22s
argocd-server-metrics                     ClusterIP   10.101.141.158   <none>        8083/TCP                     2m22s
```

## Accessing ArgoCD UI

### 1. Get Initial Admin Password

ArgoCD creates an initial admin user with a randomly generated password stored in a Kubernetes secret.

```bash
kubectl -n argocd get secret argocd-initial-admin-secret -o yaml
```

**Output:**
```yaml
apiVersion: v1
data:
  password: ay1jOXpMdkNxVzNmdFR5TQ==
kind: Secret
metadata:
  creationTimestamp: "2025-09-21T17:43:41Z"
  name: argocd-initial-admin-secret
  namespace: argocd
  resourceVersion: "827"
  uid: 626d61a6-bab6-4a49-ba2e-20e8dc064f22
type: Opaque
```

### 2. Decode the Password

The password is base64 encoded. Decode it to get the actual password:

```bash
echo "ay1jOXpMdkNxVzNmdFR5TQ==" | base64 -d
```

**Output:**
```
k-c9zLvCqW3ftTyM
```

### 3. Port Forward to Access UI

Since ArgoCD server is running as a ClusterIP service, we need to create a port forward to access it locally:

```bash
kubectl -n argocd port-forward svc/argocd-server 8080:443
```

**Output:**
```
Forwarding from 127.0.0.1:8080 -> 8080
Forwarding from [::1]:8080 -> 8080
```

### 4. Access the Web UI

Open your browser and navigate to: `https://localhost:8080`

**Login Credentials:**
- **Username:** `admin`
- **Password:** `k-c9zLvCqW3ftTyM` (the decoded password from step 2)

**Note:** You may see a certificate warning. This is normal for local development. Accept the certificate to proceed.

## Creating Applications via UI

### 1. Create New Application

1. Click the **"+ NEW APP"** button in the ArgoCD UI
2. Fill in the application details:

**Application Configuration:**
- **Application Name:** `helm-guestbook`
- **Project Name:** `default` (leave as default)
- **Sync Policy:** `Manual` (we'll sync manually for this demo)

**Source Configuration:**
- **Repository URL:** `https://github.com/argoproj/argocd-example-apps.git`
- **Path:** `helm-guestbook`

**Destination Configuration:**
- **Cluster URL:** `https://kubernetes.default.svc`
- **Namespace:** `argocd`

3. Click **"CREATE"** to create the application

### 2. Synchronize the Application

After creating the application, you'll see it in the ArgoCD UI with an "OutOfSync" status. To deploy the application:

1. Click on the `helm-guestbook` application
2. Click the **"SYNC"** button
3. Review the sync options and click **"SYNCHRONIZE"**

### 3. Verify Deployment

Check that the application pods are running:

```bash
kubectl -n argocd get po
```

**Expected Output:**
```
NAME                                                READY   STATUS    RESTARTS      AGE
argocd-application-controller-0                     1/1     Running   0             31m
argocd-applicationset-controller-54f96997f8-g8bsn   1/1     Running   0             31m
argocd-dex-server-798cbff4c7-ngp9n                  1/1     Running   1 (30m ago)   31m
argocd-notifications-controller-644f66f7df-hlg6z    1/1     Running   0             31m
argocd-redis-6684c6947f-gj4lc                       1/1     Running   0             31m
argocd-repo-server-6fccc5759b-zhgrg                 1/1     Running   0             31m
argocd-server-64d5fcbd58-4l5lh                      1/1     Running   0             31m
helm-guestbook-667dffd5cf-8xbn2                     1/1     Running   0             3m55s
```

Notice the new `helm-guestbook-667dffd5cf-8xbn2` pod that was created by ArgoCD.

### 4. Access the Guestbook Application

Check the services to see the guestbook service:

```bash
kubectl -n argocd get svc
```

**Expected Output:**
```
NAME                                      TYPE        CLUSTER-IP       EXTERNAL-IP   PORT(S)                      AGE
argocd-applicationset-controller          ClusterIP   10.103.55.225    <none>        7000/TCP,8080/TCP            32m
argocd-dex-server                         ClusterIP   10.102.64.189    <none>        5556/TCP,5557/TCP,5558/TCP   32m
argocd-metrics                            ClusterIP   10.110.212.115   <none>        8082/TCP                     32m
argocd-notifications-controller-metrics   ClusterIP   10.99.48.57      <none>        9001/TCP                     32m
argocd-redis                              ClusterIP   10.98.195.235    <none>        6379/TCP                     32m
argocd-repo-server                        ClusterIP   10.107.188.129   <none>        8081/TCP,8084/TCP            32m
argocd-server                             ClusterIP   10.110.13.100    <none>        80/TCP,443/TCP               32m
argocd-server-metrics                     ClusterIP   10.101.141.158   <none>        8083/TCP                     32m
helm-guestbook                            ClusterIP   10.103.25.8      <none>        80/TCP                       5m2s
```

Port forward to access the guestbook application:

```bash
kubectl -n argocd port-forward svc/helm-guestbook 9090:80
```

**Output:**
```
Forwarding from 127.0.0.1:9090 -> 80
Forwarding from [::1]:9090 -> 80
```

Access the application at: `http://localhost:9090`

## ArgoCD CLI

### 1. Install ArgoCD CLI

```bash
sudo curl -sSL -o /usr/local/bin/argocd https://github.com/argoproj/argo-cd/releases/latest/download/argocd-linux-amd64
sudo chmod +x /usr/local/bin/argocd
```

### 2. Login to ArgoCD

```bash
argocd login localhost:8080
```

**Interactive Output:**
```
WARNING: server certificate had error: tls: failed to verify certificate: x509: certificate signed by unknown authority. Proceed insecurely (y/n)? y
Username: admin
Password: 
'admin:login' logged in successfully
Context 'localhost:8080' updated
```

### 3. Create Application via CLI

```bash
argocd app create helm-guestbook \
  --repo https://github.com/argoproj/argocd-example-apps.git \
  --path helm-guestbook \
  --dest-server https://kubernetes.default.svc \
  --dest-namespace argocd
```

**Output:**
```
application 'helm-guestbook' created
```

### 4. Synchronize Application via CLI

```bash
argocd app sync helm-guestbook
```

**Expected Output:**
```
apps   Deployment  argocd     helm-guestbook  Synced                deployment.apps/helm-guestbook created
```

## Application Management

### Deleting Applications

#### Via UI:
1. Select the application in the ArgoCD UI
2. Click the "Delete" button
3. Confirm the deletion

#### Via CLI:
```bash
argocd app delete helm-guestbook
```

**Interactive Output:**
```
Are you sure you want to delete 'helm-guestbook' and all its resources? [y/n] y
application 'helm-guestbook' deleted
```

### Verify Deletion

After deletion, check that the application pods are removed:

```bash
kubectl -n argocd get po
```

**Expected Output:**
```
NAME                                                READY   STATUS    RESTARTS      AGE
argocd-application-controller-0                     1/1     Running   0             37m
argocd-applicationset-controller-54f96997f8-g8bsn   1/1     Running   0             37m
argocd-dex-server-798cbff4c7-ngp9n                  1/1     Running   1 (36m ago)   37m
argocd-notifications-controller-644f66f7df-hlg6z    1/1     Running   0             37m
argocd-redis-6684c6947f-gj4lc                       1/1     Running   0             37m
argocd-repo-server-6fccc5759b-zhgrg                 1/1     Running   0             37m
argocd-server-64d5fcbd58-4l5lh                      1/1     Running   0             37m
```

Notice that the `helm-guestbook` pod is no longer present.

## Homework Assignment

### Objective
Practice ArgoCD deployment using Kustomize instead of Helm.

### Task
Deploy the same guestbook application using Kustomize manifests from the ArgoCD example apps repository.

### Repository and Path
- **Repository URL:** `https://github.com/argoproj/argocd-example-apps.git`
- **Path:** `kustomize-guestbook`

### Instructions
1. Create a new ArgoCD application using the Kustomize guestbook example
2. Use both the UI and CLI methods to create the application
3. Synchronize the application and verify it's running
4. Access the application and test its functionality
5. Delete the application when done

### Expected Learning Outcomes
- Understand the difference between Helm and Kustomize deployments
- Practice creating ArgoCD applications with different source types
- Gain experience with both UI and CLI workflows
- Learn to verify application deployments and access them

### Resources
- [Kustomize Guestbook Example](https://github.com/argoproj/argocd-example-apps/tree/master/kustomize-guestbook)
- [ArgoCD Documentation](https://argo-cd.readthedocs.io/)
- [Kustomize Documentation](https://kustomize.io/)

## Summary

In this lesson, we learned:

1. **ArgoCD Installation**: How to install ArgoCD in a Kubernetes cluster
2. **UI Access**: How to access the ArgoCD web interface and retrieve admin credentials
3. **Application Creation**: How to create applications using both the web UI and CLI
4. **GitOps Workflow**: How ArgoCD monitors Git repositories and syncs applications
5. **Application Management**: How to synchronize, monitor, and delete applications
6. **CLI Usage**: How to use the ArgoCD CLI for automation and scripting

### Key Concepts
- **GitOps**: Using Git as the single source of truth for application deployments
- **Declarative Management**: Describing desired state rather than imperative commands
- **Continuous Sync**: ArgoCD continuously monitors and maintains application state
- **Multi-format Support**: ArgoCD supports various deployment formats (Helm, Kustomize, plain YAML)

### Next Steps
- Practice with the homework assignment using Kustomize
- Explore ArgoCD's advanced features like ApplicationSets and multi-cluster management
- Learn about ArgoCD's security features and RBAC configuration
- Experiment with automated sync policies and health checks

---

**Note:** This guide is based on a hands-on lesson. Always ensure you have proper permissions and understand the implications of deploying applications in your target environment.
