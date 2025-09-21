# ArgoCD Homework Solution: Kustomize Guestbook Deployment

## Overview

This document provides a complete solution for the ArgoCD homework assignment: deploying the guestbook application using Kustomize instead of Helm.

## Prerequisites

Before starting, ensure you have:
- ArgoCD installed and running (from the main lesson)
- ArgoCD CLI installed
- Access to ArgoCD UI at `https://localhost:8080`
- Admin credentials (username: `admin`, password from the lesson)

## Solution Steps

### Method 1: Using ArgoCD Web UI

#### Step 1: Access ArgoCD UI

1. Ensure ArgoCD is running and port-forward is active:
   ```bash
   kubectl -n argocd port-forward svc/argocd-server 8080:443
   ```

2. Open browser and navigate to: `https://localhost:8080`
3. Login with admin credentials

#### Step 2: Create New Application

1. Click **"+ NEW APP"** button
2. Fill in the application details:

**Application Configuration:**
- **Application Name:** `kustomize-guestbook`
- **Project Name:** `default`
- **Sync Policy:** `Manual`

**Source Configuration:**
- **Repository URL:** `https://github.com/argoproj/argocd-example-apps.git`
- **Path:** `kustomize-guestbook`

**Destination Configuration:**
- **Cluster URL:** `https://kubernetes.default.svc`
- **Namespace:** `argocd`

3. Click **"CREATE"**

#### Step 3: Synchronize Application

1. Click on the `kustomize-guestbook` application
2. Click **"SYNC"** button
3. Review sync options and click **"SYNCHRONIZE"**

#### Step 4: Verify Deployment

Check that the application is running:
```bash
kubectl -n argocd get po
```

**Expected Output:**
```
NAME                                                READY   STATUS    RESTARTS      AGE
argocd-application-controller-0                     1/1     Running   0             45m
argocd-applicationset-controller-54f96997f8-g8bsn   1/1     Running   0             45m
argocd-dex-server-798cbff4c7-ngp9n                  1/1     Running   1 (44m ago)   45m
argocd-notifications-controller-644f66f7df-hlg6z    1/1     Running   0             45m
argocd-redis-6684c6947f-gj4lc                       1/1     Running   0             45m
argocd-repo-server-6fccc5759b-zhgrg                 1/1     Running   0             45m
argocd-server-64d5fcbd58-4l5lh                      1/1     Running   0             45m
guestbook-ui-7d4b8b8b8b-xxxxx                       1/1     Running   0             2m
guestbook-ui-7d4b8b8b8b-yyyyy                       1/1     Running   0             2m
guestbook-ui-7d4b8b8b8b-zzzzz                       1/1     Running   0             2m
```

#### Step 5: Access the Application

Check services:
```bash
kubectl -n argocd get svc
```

**Expected Output:**
```
NAME                                      TYPE        CLUSTER-IP       EXTERNAL-IP   PORT(S)                      AGE
argocd-applicationset-controller          ClusterIP   10.103.55.225    <none>        7000/TCP,8080/TCP            45m
argocd-dex-server                         ClusterIP   10.102.64.189    <none>        5556/TCP,5557/TCP,5558/TCP   45m
argocd-metrics                            ClusterIP   10.110.212.115   <none>        8082/TCP                     45m
argocd-notifications-controller-metrics   ClusterIP   10.99.48.57      <none>        9001/TCP                     45m
argocd-redis                              ClusterIP   10.98.195.235    <none>        6379/TCP                     45m
argocd-repo-server                        ClusterIP   10.107.188.129   <none>        8081/TCP,8084/TCP            45m
argocd-server                             ClusterIP   10.110.13.100    <none>        80/TCP,443/TCP               45m
argocd-server-metrics                     ClusterIP   10.101.141.158   <none>        8083/TCP                     45m
guestbook-ui                              ClusterIP   10.103.25.9      <none>        80/TCP                       3m
```

Port forward to access the application:
```bash
kubectl -n argocd port-forward svc/guestbook-ui 8081:80
```

Access the application at: `http://localhost:8081`

### Method 2: Using ArgoCD CLI

#### Step 1: Login to ArgoCD CLI

```bash
argocd login localhost:8080
```

**Interactive Output:**
```
WARNING: server certificate had error: tls: failed to verify certificate: x509: certificate signed by unknown authority. Proceed insecurely (y/n)? y
Username: admin
Password: [enter your admin password]
'admin:login' logged in successfully
Context 'localhost:8080' updated
```

#### Step 2: Create Application via CLI

```bash
argocd app create kustomize-guestbook \
  --repo https://github.com/argoproj/argocd-example-apps.git \
  --path kustomize-guestbook \
  --dest-server https://kubernetes.default.svc \
  --dest-namespace argocd
```

**Expected Output:**
```
application 'kustomize-guestbook' created
```

#### Step 3: Synchronize Application

```bash
argocd app sync kustomize-guestbook
```

**Expected Output:**
```
apps   Deployment  argocd     kustomize-guestbook  Synced                deployment.apps/guestbook-ui created
apps   Service     argocd     kustomize-guestbook  Synced                service/guestbook-ui created
```

#### Step 4: Verify Application Status

```bash
argocd app get kustomize-guestbook
```

**Expected Output:**
```
Name:               kustomize-guestbook
Project:            default
Server:             https://kubernetes.default.svc
Namespace:          argocd
URL:                https://localhost:8080/applications/kustomize-guestbook
Repo:               https://github.com/argoproj/argocd-example-apps.git
Target:             HEAD
Path:               kustomize-guestbook
SyncWindow:         Sync Allowed
Sync Policy:        <none>
Sync Status:        Synced to HEAD (abc1234)
Health Status:      Healthy

GROUP  KIND        NAMESPACE  NAME           STATUS  HEALTH   HOOK  MESSAGE
apps   Deployment  argocd     guestbook-ui   Synced  Healthy        deployment.apps/guestbook-ui created
       Service     argocd     guestbook-ui   Synced  Healthy        service/guestbook-ui created
```

## Understanding the Kustomize Structure

Let's examine what makes this deployment different from the Helm version:

### Repository Structure
```
kustomize-guestbook/
├── kustomization.yaml
├── guestbook-ui-deployment.yaml
└── guestbook-ui-service.yaml
```

### Key Files

**kustomization.yaml:**
```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

resources:
- guestbook-ui-deployment.yaml
- guestbook-ui-service.yaml

commonLabels:
  app.kubernetes.io/name: guestbook-ui
  app.kubernetes.io/part-of: kustomize-guestbook
```

**guestbook-ui-deployment.yaml:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: guestbook-ui
spec:
  replicas: 3
  selector:
    matchLabels:
      app: guestbook-ui
  template:
    metadata:
      labels:
        app: guestbook-ui
    spec:
      containers:
      - name: guestbook-ui
        image: gcr.io/google-samples/gb-frontend:v4
        ports:
        - containerPort: 80
```

**guestbook-ui-service.yaml:**
```yaml
apiVersion: v1
kind: Service
metadata:
  name: guestbook-ui
spec:
  selector:
    app: guestbook-ui
  ports:
  - port: 80
    targetPort: 80
  type: ClusterIP
```

## Testing the Application

### 1. Access the Guestbook

With port forwarding active (`kubectl -n argocd port-forward svc/guestbook-ui 8081:80`), open your browser to `http://localhost:8081`.

### 2. Test Functionality

1. You should see a guestbook interface
2. Try adding a guest entry
3. Verify the entry appears in the list
4. Test multiple entries to ensure the application is working correctly

### 3. Verify Pod Scaling

Check that multiple replicas are running:
```bash
kubectl -n argocd get pods -l app=guestbook-ui
```

**Expected Output:**
```
NAME                            READY   STATUS    RESTARTS   AGE
guestbook-ui-7d4b8b8b8b-xxxxx   1/1     Running   0          5m
guestbook-ui-7d4b8b8b8b-yyyyy   1/1     Running   0          5m
guestbook-ui-7d4b8b8b8b-zzzzz   1/1     Running   0          5m
```

## Cleanup

### Delete the Application

#### Via UI:
1. Select the `kustomize-guestbook` application
2. Click "Delete"
3. Confirm deletion

#### Via CLI:
```bash
argocd app delete kustomize-guestbook
```

**Interactive Output:**
```
Are you sure you want to delete 'kustomize-guestbook' and all its resources? [y/n] y
application 'kustomize-guestbook' deleted
```

### Verify Cleanup

```bash
kubectl -n argocd get po
```

The guestbook pods should be removed, leaving only the ArgoCD system pods.

## Key Differences: Helm vs Kustomize

| Aspect | Helm | Kustomize |
|--------|------|-----------|
| **Configuration** | Templates with values | Plain YAML with overlays |
| **Customization** | Values files | Kustomization files |
| **Learning Curve** | Steeper (templating) | Gentler (plain YAML) |
| **GitOps Integration** | Native support | Native support |
| **ArgoCD Support** | Full support | Full support |
| **Use Case** | Complex applications | Simple to moderate applications |

## Troubleshooting

### Common Issues

#### 1. Application Stuck in "OutOfSync" Status

**Solution:**
```bash
argocd app sync kustomize-guestbook --force
```

#### 2. Pods Not Starting

**Check pod logs:**
```bash
kubectl -n argocd logs -l app=guestbook-ui
```

**Check pod status:**
```bash
kubectl -n argocd describe pod -l app=guestbook-ui
```

#### 3. Service Not Accessible

**Verify service endpoints:**
```bash
kubectl -n argocd get endpoints guestbook-ui
```

**Check service selector:**
```bash
kubectl -n argocd get svc guestbook-ui -o yaml
```

#### 4. Port Forward Issues

**Kill existing port forwards:**
```bash
pkill -f "kubectl.*port-forward"
```

**Start fresh port forward:**
```bash
kubectl -n argocd port-forward svc/guestbook-ui 8081:80
```

## Verification Checklist

- [ ] ArgoCD is running and accessible
- [ ] Application created successfully (UI or CLI)
- [ ] Application synchronized without errors
- [ ] Pods are running and healthy
- [ ] Service is created and accessible
- [ ] Application is accessible via browser
- [ ] Guestbook functionality works (add/view entries)
- [ ] Multiple replicas are running
- [ ] Application can be deleted cleanly

## Learning Outcomes

After completing this homework, you should understand:

1. **Kustomize vs Helm**: The differences between these two deployment approaches
2. **ArgoCD Flexibility**: How ArgoCD supports multiple deployment formats
3. **GitOps Workflow**: The complete cycle of Git-based deployments
4. **Application Management**: Both UI and CLI approaches to managing applications
5. **Troubleshooting**: Common issues and their solutions
6. **Verification**: How to ensure deployments are working correctly

## Next Steps

1. **Explore Advanced Features**: Try ApplicationSets for managing multiple applications
2. **Multi-Environment**: Deploy the same application to different namespaces
3. **Automated Sync**: Configure automatic synchronization policies
4. **Health Checks**: Implement custom health checks for applications
5. **RBAC**: Configure role-based access control for team members

---

**Note:** This solution assumes you have completed the main ArgoCD lesson and have a working ArgoCD installation. If you encounter issues, refer to the troubleshooting section or the main student guide.
