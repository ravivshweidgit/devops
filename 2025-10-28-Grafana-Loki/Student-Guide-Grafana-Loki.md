# Grafana Loki - Complete Student Guide

## Table of Contents
1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Environment Setup](#environment-setup)
4. [Loki Stack Installation](#loki-stack-installation)
5. [Configuration Files](#configuration-files)
6. [Accessing Grafana](#accessing-grafana)
7. [Log Collection and Visualization](#log-collection-and-visualization)
8. [Advanced Configuration](#advanced-configuration)
9. [Dashboard Import](#dashboard-import)
10. [Troubleshooting](#troubleshooting)
11. [Best Practices](#best-practices)

## Overview

This lesson covers the complete setup and configuration of **Grafana Loki**, a horizontally-scalable, highly-available log aggregation system inspired by Prometheus. Loki is designed to be very cost-effective and easy to operate, as it does not index the contents of the logs, but rather a set of labels for each log stream.

### What You'll Learn
- How to deploy Loki stack on Kubernetes using Helm
- Configure log collection with Promtail
- Set up Grafana for log visualization
- Create custom log generators for testing
- Configure advanced Promtail settings with custom labels
- Import and use pre-built dashboards

## Prerequisites

Before starting this lesson, ensure you have:
- **Minikube** installed and running
- **kubectl** configured to work with your cluster
- **Helm** installed
- Basic understanding of Kubernetes concepts
- Basic knowledge of YAML configuration files

## Environment Setup

### Step 1: Clean Environment
Start with a fresh Minikube environment:

```bash
# Delete existing cluster
minikube delete

# Start new cluster
minikube start
```

### Step 2: Install Helm
Install Helm package manager:

```bash
sudo snap install helm --classic
```

## Loki Stack Installation

### Step 1: Create Loki Values Configuration

Create a file named `loki-values.yaml` with the following configuration:

```yaml
loki:
  enabled: true
  isDefault: true
  url: http://{{(include "loki.serviceName" .)}}:{{ .Values.loki.service.port }}
  readinessProbe:
    httpGet:
      path: /ready
      port: http-metrics
    initialDelaySeconds: 45
  livenessProbe:
    httpGet:
      path: /ready
      port: http-metrics
    initialDelaySeconds: 45
  datasource:
    jsonData: "{}"
    uid: ""

promtail:
  enabled: true
  config:
    logLevel: info
    serverPort: 3101
    clients:
      - url: http://{{ .Release.Name }}:3100/loki/api/v1/push

grafana:
  enabled: true
  sidecar:
    datasources:
      label: ""
      labelValue: ""
      enabled: true
      maxLines: 1000
  image:
    tag: latest
```

### Step 2: Deploy Loki Stack

Deploy the complete Loki stack using Helm:

```bash
helm upgrade --install loki -f loki-values.yaml -n logging --create-namespace grafana/loki-stack
```

**Expected Output:**
```
Release "loki" does not exist. Installing it now.
NAME: loki
LAST DEPLOYED: Wed Oct 29 20:31:20 2025
NAMESPACE: logging
STATUS: deployed
REVISION: 1
NOTES:
The Loki stack has been deployed to your cluster. Loki can now be added as a datasource in Grafana.
```

### Step 3: Verify Deployment

Check that all pods are running:

```bash
kubectl get pods -n logging
```

**Expected Output:**
```
NAME                            READY   STATUS    RESTARTS   AGE
loki-0                          1/1     Running   0          90s
loki-grafana-565bd659b7-j7wff   2/2     Running   0          90s
loki-promtail-bvd28             1/1     Running   0          90s
```

Check services:

```bash
kubectl get svc -n logging
```

**Expected Output:**
```
NAME              TYPE        CLUSTER-IP       EXTERNAL-IP   PORT(S)    AGE
loki              ClusterIP   10.96.215.69     <none>        3100/TCP   3m7s
loki-grafana      ClusterIP   10.103.179.129   <none>        80/TCP     3m7s
loki-headless     ClusterIP   None             <none>        3100/TCP   3m7s
loki-memberlist   ClusterIP   None             <none>        7946/TCP   3m7s
```

## Configuration Files

### Understanding the Components

1. **Loki**: The log aggregation system
2. **Promtail**: Log collection agent
3. **Grafana**: Visualization and dashboard interface

### Key Configuration Points

- **Loki URL**: Points to the Loki service for log ingestion
- **Promtail**: Configured to send logs to Loki
- **Grafana**: Pre-configured with Loki as a datasource

## Accessing Grafana

### Step 1: Get Admin Password

Retrieve the Grafana admin password:

```bash
kubectl get secret --namespace logging loki-grafana -o jsonpath="{.data.admin-password}"
```

Decode the base64 password:

```bash
echo "YOUR_BASE64_PASSWORD" | base64 --decode
```

### Step 2: Port Forward to Access Grafana

```bash
kubectl port-forward -n logging svc/loki-grafana 3000:80
```

### Step 3: Login to Grafana

1. Open browser and go to `http://localhost:3000`
2. Login with:
   - **Username**: `admin`
   - **Password**: `[decoded password from step 1]`

## Log Collection and Visualization

### Step 1: View Existing Logs

1. In Grafana, go to **Connections** → **Data Sources** → **Loki**
2. Click **Explore**
3. Use label filters:
   - **Label**: `pod`
   - **Value**: `kube-proxy`
4. Execute query to see logs

### Step 2: Create Test Log Generator

Create a deployment file `deployment.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: log-generator
  labels:
    app: log-generator
spec:
  replicas: 1
  selector:
    matchLabels:
      app: log-generator
  template:
    metadata:
      labels:
        app: log-generator
    spec:
      containers:
        - name: log-generator
          image: busybox
          command:
            - /bin/sh
            - -c
            - |
              while true; do
                echo "$(date) - Test log message from log-generator"
                sleep 5
              done
```

Deploy the log generator:

```bash
kubectl apply -f deployment.yaml
```

### Step 3: View Generated Logs

1. Back in Grafana, refresh the page (F5)
2. Use label filters:
   - **Label**: `pod`
   - **Value**: `log-generator`
3. You should see the generated test logs at the bottom

## Advanced Configuration

### Step 1: Create Custom Promtail Configuration

Create `loki-secret.yaml` with advanced Promtail configuration:

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: loki-promtail
  namespace: logging
  labels:
    app: promtail
type: Opaque
stringData:
  promtail.yaml: |
    server:
      log_level: info
      log_format: logfmt
      http_listen_port: 3101

    clients:
      - url: http://loki:3100/loki/api/v1/push

    positions:
      filename: /run/promtail/positions.yaml

    scrape_configs:
      - job_name: kubernetes-pods
        pipeline_stages:
          - cri: {}
          - match:
              selector: '{app="log-generator"}'
              stages:
                - json:
                    expressions:
                      stream: stream
                      time: time
                - labels:
                    stream:
                    time:
        kubernetes_sd_configs:
          - role: pod
        relabel_configs:
          - source_labels:
              - __meta_kubernetes_pod_controller_name
            regex: ([0-9a-z-.]+?)(-[0-9a-f]{8,10})?
            action: replace
            target_label: __tmp_controller_name
          - source_labels:
              - __meta_kubernetes_pod_label_app_kubernetes_io_name
              - __meta_kubernetes_pod_label_app
              - __tmp_controller_name
              - __meta_kubernetes_pod_name
            regex: ^;*([^;]+)(;.*)?$
            action: replace
            target_label: app
          - source_labels:
              - __meta_kubernetes_pod_label_app_kubernetes_io_instance
              - __meta_kubernetes_pod_label_instance
            regex: ^;*([^;]+)(;.*)?$
            action: replace
            target_label: instance
          - source_labels:
              - __meta_kubernetes_pod_label_app_kubernetes_io_component
              - __meta_kubernetes_pod_label_component
            regex: ^;*([^;]+)(;.*)?$
            action: replace
            target_label: component
          - action: replace
            source_labels:
            - __meta_kubernetes_pod_node_name
            target_label: node_name
          - action: replace
            source_labels:
            - __meta_kubernetes_namespace
            target_label: namespace
          - action: replace
            replacement: $1
            separator: /
            source_labels:
            - namespace
            - app
            target_label: job
          - action: replace
            source_labels:
            - __meta_kubernetes_pod_name
            target_label: pod
          - action: replace
            source_labels:
            - __meta_kubernetes_pod_container_name
            target_label: container
          - action: replace
            replacement: /var/log/pods/*$1/*.log
            separator: /
            source_labels:
            - __meta_kubernetes_pod_uid
            - __meta_kubernetes_pod_container_name
            target_label: __path__
          - action: replace
            regex: true/(.*)
            replacement: /var/log/pods/*$1/*.log
            separator: /
            source_labels:
            - __meta_kubernetes_pod_annotationpresent_kubernetes_io_config_hash
            - __meta_kubernetes_pod_annotation_kubernetes_io_config_hash
            - __meta_kubernetes_pod_container_name
            target_label: __path__

    limits_config:

    tracing:
      enabled: false
```

### Step 2: Apply Custom Configuration

1. Delete the existing Promtail secret:
```bash
kubectl delete secret loki-promtail -n logging
```

2. Apply the new configuration:
```bash
kubectl apply -f loki-secret.yaml
```

3. Restart Promtail pod to apply new configuration:
```bash
kubectl get pod -n logging
kubectl delete pod loki-promtail-[POD_ID] -n logging
```

### Step 3: Verify New Labels

1. Refresh Grafana (F5)
2. You should now see two new labels: `stream` and `time`
3. These labels are extracted from the log content using the JSON pipeline stage

## Dashboard Import

### Step 1: Import Pre-built Dashboard

1. In Grafana, go to **Dashboards** → **Import**
2. Use dashboard ID: `15141`
3. This is the "Kubernetes Service Logs" dashboard from Grafana.com
4. URL: https://grafana.com/grafana/dashboards/15141-kubernetes-service-logs/

### Step 2: Configure Dashboard

1. Select your Loki datasource
2. The dashboard will automatically populate with your cluster's log data
3. Explore different visualizations and filters

## Troubleshooting

### Common Issues and Solutions

#### 1. Pods Not Starting
```bash
# Check pod status
kubectl get pods -n logging

# Check pod logs
kubectl logs -n logging [POD_NAME]

# Check events
kubectl get events -n logging --sort-by='.lastTimestamp'
```

#### 2. Cannot Access Grafana
```bash
# Check if port-forward is running
kubectl port-forward -n logging svc/loki-grafana 3000:80

# Check service status
kubectl get svc -n logging
```

#### 3. No Logs Appearing
```bash
# Check Promtail logs
kubectl logs -n logging -l app=promtail

# Verify log generator is running
kubectl get pods | grep log-generator

# Check if logs are being generated
kubectl logs -l app=log-generator
```

#### 4. Configuration Not Applied
```bash
# Verify secret was created
kubectl get secret -n logging loki-promtail

# Check Promtail configuration
kubectl get secret -n logging loki-promtail -o yaml
```

### Useful Commands

```bash
# Check all resources in logging namespace
kubectl get all -n logging

# Describe a specific resource
kubectl describe pod [POD_NAME] -n logging

# Check Helm releases
helm list -n logging

# View Helm values
helm get values loki -n logging
```

## Best Practices

### 1. Resource Management
- Monitor resource usage of Loki and Promtail
- Set appropriate resource limits and requests
- Consider using persistent volumes for Loki data

### 2. Log Retention
- Configure log retention policies
- Use appropriate storage backends for production
- Monitor storage usage

### 3. Security
- Use proper RBAC configurations
- Secure Grafana access
- Consider using TLS for production deployments

### 4. Monitoring
- Set up alerts for log collection failures
- Monitor Loki and Promtail health
- Use Grafana dashboards for observability

### 5. Performance
- Tune Promtail configuration for your environment
- Use appropriate log levels
- Consider log sampling for high-volume environments

## Summary

In this lesson, you learned how to:

1. ✅ Set up a complete Loki stack on Kubernetes
2. ✅ Configure log collection with Promtail
3. ✅ Access and use Grafana for log visualization
4. ✅ Create test log generators
5. ✅ Configure advanced Promtail settings with custom labels
6. ✅ Import and use pre-built dashboards

### Next Steps

- Experiment with different log sources
- Create custom dashboards
- Set up alerting rules
- Explore advanced Loki features like log parsing and filtering
- Consider production deployment strategies

### Additional Resources

- [Loki Documentation](https://grafana.com/docs/loki/latest/)
- [Promtail Configuration](https://grafana.com/docs/loki/latest/clients/promtail/configuration/)
- [Grafana Loki Dashboards](https://grafana.com/grafana/dashboards/?search=loki)
- [Kubernetes Logging Best Practices](https://kubernetes.io/docs/concepts/cluster-administration/logging/)

---

**Note**: This guide assumes a learning environment. For production deployments, additional considerations for security, scalability, and reliability should be implemented.
