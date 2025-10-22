# Prometheus Monitoring with Kubernetes - Student Guide

## Table of Contents
1. [Introduction](#introduction)
2. [Prerequisites](#prerequisites)
3. [Installing Prometheus Stack with Helm](#installing-prometheus-stack-with-helm)
4. [Verifying Installation](#verifying-installation)
5. [Accessing Prometheus UI](#accessing-prometheus-ui)
6. [Custom Alert Rules](#custom-alert-rules)
7. [Testing Alerts](#testing-alerts)
8. [Prometheus Sharding](#prometheus-sharding)
9. [Thanos Integration](#thanos-integration)
10. [Troubleshooting](#troubleshooting)

## Introduction

This guide covers setting up a complete Prometheus monitoring stack in Kubernetes, including:
- Prometheus server for metrics collection
- Alertmanager for alert handling
- Custom alert rules
- Prometheus sharding for scalability
- Thanos for long-term storage and querying

## Prerequisites

- Kubernetes cluster (minikube, kind, or cloud provider)
- Helm 3.x installed
- kubectl configured
- Docker (for local development)

## Installing Prometheus Stack with Helm

### Step 1: Add Prometheus Community Helm Repository

```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
```

### Step 2: Update Helm Repositories

```bash
helm repo update
```

### Step 3: Install kube-prometheus-stack

```bash
helm install kube-prometheus-stack \
  --create-namespace \
  --namespace kube-prometheus-stack \
  prometheus-community/kube-prometheus-stack
```

This command will:
- Create a new namespace called `kube-prometheus-stack`
- Install Prometheus, Alertmanager, Grafana, and kube-state-metrics
- Set up service monitors and alerting rules

## Verifying Installation

### Check Pod Status

```bash
kubectl get po -n kube-prometheus-stack
```

Expected output:
```
NAME                                                        READY   STATUS    RESTARTS   AGE
alertmanager-kube-prometheus-stack-alertmanager-0           2/2     Running   0          2m5s
kube-prometheus-stack-grafana-59b856967d-z95tx              3/3     Running   0          2m23s
kube-prometheus-stack-kube-state-metrics-557fd457c6-5kb2f   1/1     Running   0          2m23s
kube-prometheus-stack-operator-698674bb67-v87x4             1/1     Running   0          2m23s
kube-prometheus-stack-prometheus-node-exporter-dcrfj        1/1     Running   0          2m23s
prometheus-kube-prometheus-stack-prometheus-0               2/2     Running   0          2m5s
```

### Check Services

```bash
kubectl get svc -n kube-prometheus-stack
```

Expected output:
```
NAME                                             TYPE        CLUSTER-IP       EXTERNAL-IP   PORT(S)                      AGE
alertmanager-operated                            ClusterIP   None             <none>        9093/TCP,9094/TCP,9094/UDP   3m44s
kube-prometheus-stack-alertmanager               ClusterIP   10.103.132.244   <none>        9093/TCP,8080/TCP            4m3s
kube-prometheus-stack-grafana                    ClusterIP   10.101.135.100   <none>        80/TCP                       4m3s
kube-prometheus-stack-kube-state-metrics         ClusterIP   10.96.27.232     <none>        8080/TCP                     4m3s
kube-prometheus-stack-operator                   ClusterIP   10.101.192.124   <none>        443/TCP                      4m3s
kube-prometheus-stack-prometheus                 ClusterIP   10.102.61.144    <none>        9090/TCP,8080/TCP            4m3s
kube-prometheus-stack-prometheus-node-exporter   ClusterIP   10.106.141.238   <none>        9100/TCP                     4m3s
prometheus-operated                              ClusterIP   None             <none>        9090/TCP                     3m44s
```

## Accessing Prometheus UI

### Port Forward to Prometheus

```bash
kubectl port-forward -n kube-prometheus-stack svc/kube-prometheus-stack-prometheus 9090:9090
```

Access Prometheus at: http://localhost:9090/

### Port Forward to Alertmanager

```bash
kubectl port-forward -n kube-prometheus-stack svc/kube-prometheus-stack-alertmanager 9093:9093
```

Access Alertmanager at: http://localhost:9093/

## Custom Alert Rules

### Creating Custom Alert Rules

Create a file called `custom-alert-rules.yaml`:

```yaml
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: kube-pod-not-ready
  namespace: kube-prometheus-stack
spec:
  groups:
  - name: kubernetes-pods
    rules:
    - alert: KubernetesPodNotHealthy
      expr: |
        sum(kube_pod_status_phase{phase="Unknown"}) by (namespace, pod) or 
        (count(kube_pod_deletion_timestamp) by (namespace, pod) * 
         sum(kube_pod_status_reason{reason="NodeLost"}) by(namespace, pod))
      for: 15m
      labels:
        severity: critical
      annotations:
        summary: "Kubernetes Pod not healthy (instance {{ $labels.instance }})"
        description: "Pod {{ $labels.namespace }}/{{ $labels.pod }} has been in a non-running state for longer than 15 minutes. VALUE = {{ $value }} LABELS = {{ $labels }}"
```

### Apply Custom Alert Rules

```bash
kubectl apply -f custom-alert-rules.yaml
```

## Testing Alerts

### Create a Failing Pod

```bash
kubectl run nginx-pod --image=nginx:lates3
```

This will create a pod with an invalid image that will fail to start.

### Check Pod Status

```bash
kubectl get pods
```

Expected output:
```
NAME        READY   STATUS         RESTARTS   AGE
nginx-pod   0/1     ErrImagePull   0          39s
```

### Verify Alert in Prometheus

1. Go to http://localhost:9090/alerts
2. Look for the "KubernetesPodNotHealthy" alert
3. The alert should show as "Active" with the following labels:
   - alertname="KubernetesPodNotHealthy"
   - namespace="default"
   - pod="nginx-pod"
   - severity="critical"

### Clean Up Test Pod

```bash
kubectl delete pod nginx-pod
```

The alert should resolve once the pod is deleted.

## Prometheus Sharding

### Setting Up Sample Applications

First, navigate to the prometheus directory and start the sample applications:

```bash
cd prometheus/
```

Start the sample applications:

```bash
docker compose up -d --build go-application
docker compose up -d --build python-application
docker compose up -d --build dotnet-application
docker compose up -d --build nodejs-application
```

### Setting Up Prometheus Sharding

Navigate to the sharding directory:

```bash
cd sharding/
```

### Start Sharded Prometheus Instances

```bash
docker compose up -d prometheus-00
docker compose up -d prometheus-01
```

### Verify Sharded Instances

```bash
docker ps
```

Expected output:
```
CONTAINER ID   IMAGE                    COMMAND                  CREATED          STATUS          PORTS                                         NAMES
a7d20396a583   prom/prometheus:v3.3.0   "/bin/prometheus --c…"   13 seconds ago   Up 12 seconds   0.0.0.0:9091->9090/tcp, [::]:9091->9090/tcp   prometheus-01
bfa8849619ee   prom/prometheus:v3.3.0   "/bin/prometheus --c…"   18 seconds ago   Up 17 seconds   0.0.0.0:9090->9090/tcp, [::]:9090->9090/tcp   prometheus-00
```

Access the sharded instances:
- Prometheus-00: http://localhost:9090/
- Prometheus-01: http://localhost:9091/

## Thanos Integration

### Setting Up Thanos

Navigate to the Thanos directory:

```bash
cd prometheus/thanos/
```

### Start Thanos Stack

```bash
docker compose up
```

### Verify Thanos Components

```bash
docker ps
```

Expected output:
```
CONTAINER ID   IMAGE                           COMMAND                  CREATED          STATUS          PORTS                                                             NAMES
3045e3998a8e   grafana/grafana:latest          "/run.sh"                22 seconds ago   Up 21 seconds   0.0.0.0:3000->3000/tcp, [::]:3000->3000/tcp                       grafana
f7712b3d6d55   quay.io/thanos/thanos:v0.38.0   "/bin/thanos query -…"   22 seconds ago   Up 21 seconds   0.0.0.0:19090->19090/tcp, [::]:19090->19090/tcp                   thanos-query
12794378709b   quay.io/thanos/thanos:v0.38.0   "/bin/thanos sidecar…"   23 seconds ago   Up 21 seconds                                                                     thanos-sidecar-01
b9003983a39c   quay.io/thanos/thanos:v0.38.0   "/bin/thanos sidecar…"   23 seconds ago   Up 21 seconds                                                                     thanos-sidecar-00
95cb549ef0be   quay.io/minio/minio:latest      "/usr/bin/docker-ent…"   23 seconds ago   Up 22 seconds   0.0.0.0:9000-9001->9000-9001/tcp, [::]:9000-9001->9000/tcp   minio
```

### Access Thanos Query

- Thanos Query: http://localhost:19090/
- MinIO (Object Storage): http://localhost:9000/
- Grafana: http://localhost:3000/

### Access Grafana

Open Grafana in Browser:
- http://localhost:3000
- Go to http://localhost:3000/connections/datasources
- Click "Explore" to start querying metrics

## Troubleshooting

### Check Prometheus Configuration

Access the configuration through the UI:
- Go to http://localhost:9090/config

Or check the configuration in the cluster:

```bash
kubectl exec -it prometheus-kube-prometheus-stack-prometheus-0 -n kube-prometheus-stack -- /bin/sh
cat /etc/prometheus/config_out/prometheus.env.yaml
```

### Common Issues

1. **Pods not starting**: Check resource limits and node capacity
2. **Alerts not firing**: Verify alert rules syntax and evaluation time
3. **Metrics not appearing**: Check service monitor configurations
4. **Port forwarding issues**: Ensure correct service ports

### Useful Commands

```bash
# Check all resources in namespace
kubectl get all -n kube-prometheus-stack

# Check logs
kubectl logs -n kube-prometheus-stack prometheus-kube-prometheus-stack-prometheus-0

# Check events
kubectl get events -n kube-prometheus-stack

# Clean up (if needed)
minikube delete
```

## Summary

This guide covered:
1. Installing Prometheus stack with Helm
2. Setting up custom alert rules
3. Testing alert functionality
4. Implementing Prometheus sharding
5. Integrating Thanos for long-term storage
6. Accessing Grafana for visualization
7. Troubleshooting common issues

The setup provides a complete monitoring solution for Kubernetes clusters with alerting, visualization, and long-term storage capabilities.