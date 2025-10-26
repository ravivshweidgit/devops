# ELK Stack on Kubernetes with Minikube - Student Guide

## Table of Contents
1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Understanding the ELK Stack](#understanding-the-elk-stack)
4. [Getting Started](#getting-started)
5. [Deploying Elasticsearch](#deploying-elasticsearch)
6. [Deploying Kibana](#deploying-kibana)
7. [Deploying Logstash](#deploying-logstash)
8. [Deploying Filebeat](#deploying-filebeat)
9. [Final Deployment](#final-deployment)
10. [Verification](#verification)
11. [Troubleshooting](#troubleshooting)

---

## Overview

This guide will walk you through deploying a complete **ELK (Elasticsearch, Logstash, Kibana)** Stack on Kubernetes using Minikube. The ELK Stack is a powerful combination of tools for log aggregation, processing, analysis, and visualization.

### What You'll Learn
- How to deploy the ELK Stack on Kubernetes
- Understanding the interaction between different components
- Configuring ConfigMaps in Kubernetes
- Working with NodePort services in Minikube
- Setting up log collection and visualization

---

## Prerequisites

Before starting, ensure you have the following installed:

- **Minikube** - Local Kubernetes environment
- **kubectl** - Kubernetes command-line tool
- **Docker** - Container runtime
- **Git** - Version control system
- **Basic understanding** of Kubernetes concepts (Deployments, Services, ConfigMaps, Pods)

---

## Understanding the ELK Stack

The ELK Stack consists of three main components plus Filebeat:

### 1. **Elasticsearch**
- Distributed search and analytics engine
- Stores and indexes data
- RESTful search engine

### 2. **Logstash**
- Data processing pipeline
- Collects, transforms, and enriches data
- Sends processed data to Elasticsearch

### 3. **Kibana**
- Visualization and exploration platform
- Creates dashboards and visualizations
- Interacts with data in Elasticsearch

### 4. **Filebeat**
- Lightweight log shipper
- Monitors log files
- Sends logs to Logstash for processing

### Architecture Flow

```
Application Logs → Filebeat → Logstash → Elasticsearch → Kibana
```

---

## Getting Started

### Step 1: Start Minikube

First, start your Minikube cluster. Note: Allocate resources based on your system's capabilities.

```bash
# Try with 8GB memory (adjust based on your system)
minikube start --cpus 4 --memory 8192
```

**Expected Output:**
```
😄  minikube v1.35.0 on Ubuntu 24.04
✨  Automatically selected the docker driver
...
🏄  Done! kubectl is now configured to use "minikube" cluster
```

**Important Note:** If you get a memory error, reduce the memory allocation:
```bash
minikube start --cpus 4 --memory 2200mb
```

### Step 2: Clone the Repository

Navigate to your work directory and clone the ELK Stack Kubernetes repository:

```bash
cd ~/work
git clone https://github.com/sagary2j/ELK-Stack-Kubernetes-minikube
cd ELK-Stack-Kubernetes-minikube
```

### Step 3: View Repository Contents

```bash
ls
```

You should see the following files:
- `app-deployment.yml` - Application deployment configuration
- `es-deployment.yaml` - Elasticsearch deployment
- `es-svc.yaml` - Elasticsearch service
- `filebeat.yml` - Filebeat configuration
- `kibana-deployment.yaml` - Kibana deployment
- `kibana-svc.yaml` - Kibana service
- `logstash.conf` - Logstash configuration
- `logstash-deployment.yml` - Logstash deployment
- `logstash-svc.yml` - Logstash service
- `README.md` - Repository documentation

---

## Deploying Elasticsearch

Elasticsearch is the core of the ELK Stack and will store all our data.

### Step 1: Deploy Elasticsearch

```bash
kubectl apply -f es-deployment.yaml
```

**Expected Output:**
```
deployment.apps/es-logging created
```

### Step 2: Check Deployment Status

```bash
kubectl get deploy
```

**Expected Output:**
```
NAME         READY   UP-TO-DATE   AVAILABLE   AGE
es-logging   0/1     1            0           18s
```

The `0/1` indicates that the pod is still starting. Wait for it to become `1/1`.

### Step 3: Monitor Pod Status

```bash
kubectl get pods
```

Initially, you'll see:
```
NAME                          READY   STATUS    RESTARTS   AGE
es-logging-66c49458cd-j4957   0/1     Running   0          30s
```

Keep checking until the pod is ready:
```bash
kubectl get pods
```

**Ready Status:**
```
NAME                          READY   STATUS    RESTARTS   AGE
es-logging-66c49458cd-j4957   1/1     Running   0          66s
```

**Key Learning:** Elasticsearch takes some time to start because it initializes the cluster and prepares storage.

### Step 4: Create Elasticsearch Service

```bash
kubectl apply -f es-svc.yaml
```

**Expected Output:**
```
service/es-service created
```

### Step 5: View Services

```bash
kubectl get svc
```

**Expected Output:**
```
NAME         TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)          AGE
es-service   NodePort    10.98.127.246   <none>        9200:31870/TCP   12s
kubernetes   ClusterIP   10.96.0.1       <none>        443/TCP          4m10s
```

**Key Information:**
- **Port 9200** is the Elasticsearch HTTP API port
- **31870** is the NodePort mapped to your local machine
- **TYPE: NodePort** exposes the service externally via the Minikube IP

### Step 6: Access Elasticsearch

```bash
minikube service es-service
```

This will open Elasticsearch in your default browser. You can also manually access it at:
```
http://192.168.49.2:31870
```

**Verify Elasticsearch is Running:**
Visit the URL in your browser or use:
```bash
curl http://192.168.49.2:31870
```

You should see Elasticsearch cluster information.

---

## Deploying Kibana

Kibana is the visualization layer that connects to Elasticsearch.

### Step 1: Deploy Kibana

```bash
kubectl apply -f kibana-deployment.yaml
```

**Expected Output:**
```
deployment.apps/kibana-logging created
```

### Step 2: Check Pod Status

```bash
kubectl get pods
```

**Expected Output:**
```
NAME                              READY   STATUS    RESTARTS   AGE
es-logging-66c49458cd-j4957       1/1     Running   0          9m12s
kibana-logging-56d8b656cd-qkcph   1/1     Running   0          2m22s
```

### Step 3: Get Minikube IP

Kibana needs to know where Elasticsearch is running. First, get the Minikube IP:

```bash
minikube ip
```

**Expected Output:**
```
192.168.49.2
```

**Note:** Your IP might be different. Use the IP address shown in your output.

### Step 4: Configure Kibana to Connect to Elasticsearch

Set the Elasticsearch hosts environment variable for the Kibana deployment:

```bash
kubectl set env deployments/kibana-logging ELASTICSEARCH_HOSTS=http://192.168.49.2:31870
```

**Expected Output:**
```
deployment.apps/kibana-logging env updated
```

**Key Learning:** This environment variable tells Kibana where to find Elasticsearch.

### Step 5: Apply Kibana Service

```bash
kubectl apply -f kibana-svc.yaml
```

**Expected Output:**
```
service/kibana-service created
```

### Step 6: Access Kibana

```bash
minikube service kibana-service
```

**Expected Output:**
```
|-----------|----------------|-------------|---------------------------|
| NAMESPACE |      NAME      | TARGET PORT |            URL            |
|-----------|----------------|-------------|---------------------------|
| default   | kibana-service |        5601 | http://192.168.49.2:30328 |
|-----------|----------------|-------------|---------------------------|
🎉  Opening service default/kibana-service in default browser...
```

**Access Kibana at:** `http://192.168.49.2:30328`

**Key Learning:** Kibana runs on port 5601 internally, exposed through NodePort 30328 externally.

---

## Deploying Logstash

Logstash will process logs before sending them to Elasticsearch.

### Step 1: Configure Logstash

Open `logstash.conf` and update it with the following configuration:

```conf
input {
  beats {
    port => "5044"
  }
}
filter {
      if [message] =~ /^\{.*\}$/ {
        json {
          source => "message"
        }
      }
      if [ClientHost] {
        geoip {
          source => "ClientHost"
        }
      }
    }
output {
  elasticsearch {
    hosts => ["http://192.168.49.2:31870"]
    index => "%{[@metadata][beat]}-%{[@metadata][version]}-%{+YYYY.MM.dd}"
  }
  stdout {
    codec => rubydebug
  }
}
```

**Configuration Explanation:**
- **Input:** Listens on port 5044 for incoming data from Beats
- **Filter:** 
  - Parses JSON messages
  - Adds geoip information if ClientHost is present
- **Output:** 
  - Sends processed data to Elasticsearch at `http://192.168.49.2:31870`
  - Creates dynamic index names based on beat type, version, and date
  - Also outputs to stdout for debugging

### Step 2: Create Logstash ConfigMap

```bash
kubectl create configmap log-manual-pipeline --from-file ./logstash.conf
```

**Expected Output:**
```
configmap/log-manual-pipeline created
```

**Important:** The ConfigMap name (`log-manual-pipeline`) must match the name referenced in `logstash-deployment.yml`.

**Key Learning:** ConfigMaps store configuration data that pods can consume.

### Step 3: Deploy Logstash

```bash
kubectl apply -f logstash-deployment.yml
```

**Expected Output:**
```
deployment.apps/logstash-logging created
```

### Step 4: Apply Logstash Service

```bash
kubectl apply -f logstash-svc.yml
```

**Expected Output:**
```
service/logstash-service created
```

### Step 5: Verify Deployment

```bash
kubectl get pods
```

**Expected Output:**
```
NAME                               READY   STATUS    RESTARTS   AGE
es-logging-66c49458cd-j4957        1/1     Running   0          53m
kibana-logging-67c66d58dd-kscr9    1/1     Running   0          39m
logstash-logging-fc6ffb597-pv5dq   1/1     Running   0          23s
```

### Step 6: Check Services

```bash
kubectl get svc
```

**Expected Output:**
```
NAME               TYPE        CLUSTER-IP       EXTERNAL-IP   PORT(S)          AGE
es-service         NodePort    10.98.127.246    <none>        9200:31870/TCP   51m
kibana-service     NodePort    10.97.230.105    <none>        5601:30328/TCP   38m
kubernetes         ClusterIP   10.96.0.1        <none>        443/TCP          55m
logstash-service   NodePort    10.110.180.216   <none>        5044:30163/TCP   37s
```

**Key Information:**
- Logstash service is exposed on NodePort `30163`
- Port 5044 is the default Beats input port

---

## Deploying Filebeat

Filebeat is the log shipper that collects logs and sends them to Logstash.

### Step 1: Configure Filebeat

Update `filebeat.yml` with the following configuration:

```yaml
filebeat.inputs:
 - type: log
   paths:
    - /tmp/output.log
 
output:
  logstash:
    hosts: [ "192.168.49.2:30163" ]
```

**Configuration Explanation:**
- **Input:** Monitors the log file at `/tmp/output.log`
- **Output:** Sends logs to Logstash at `192.168.49.2:30163` (Minikube IP + Logstash NodePort)

### Step 2: Create Filebeat ConfigMap

```bash
kubectl create configmap beat-manual-config --from-file ./filebeat.yml
```

**Expected Output:**
```
configmap/beat-manual-config created
```

### Step 3: Verify ConfigMaps

```bash
kubectl get cm
```

**Expected Output:**
```
NAME                  DATA   AGE
beat-manual-config    1      13s
kube-root-ca.crt      1      60m
log-manual-pipeline   1      7m44s
```

**Key Learning:** You now have ConfigMaps for both Logstash and Filebeat configurations.

---

## Final Deployment

### Deploy the Application

Now deploy the application that will generate logs:

```bash
kubectl apply -f app-deployment.yml
```

**Expected Output:**
```
deployment.apps/logging-app-manual created
```

### Verify All Pods

```bash
kubectl get pods
```

You should now see all components running:
- `es-logging-*` - Elasticsearch
- `kibana-logging-*` - Kibana
- `logstash-logging-*` - Logstash
- `logging-app-manual-*` - Application generating logs

---

## Verification

### Access Kibana

```bash
minikube service kibana-service
```

### Steps to View Logs in Kibana

1. **Open Kibana** at the URL provided (e.g., `http://192.168.49.2:30328`)

2. **Create Index Pattern:**
   - Navigate to **Management** → **Stack Management** → **Index Patterns**
   - Click **Create index pattern**
   - Enter pattern: `filebeat-*` or `logstash-*`
   - Click **Next step**
   - Select `@timestamp` as the time filter
   - Click **Create index pattern**

3. **View Logs:**
   - Navigate to **Analytics** → **Discover**
   - You should see logs being collected

4. **Verify Log Flow:**
   ```
   Application → Filebeat → Logstash → Elasticsearch → Kibana
   ```

### Check Elasticsearch Indices

Access Elasticsearch API to verify indices are being created:

```bash
curl http://192.168.49.2:31870/_cat/indices?v
```

You should see indices like:
- `filebeat-<version>-YYYY.MM.DD`
- Or based on your Logstash configuration

---

## Architecture Summary

```
┌─────────────────────────────────────────────────────────────┐
│                    Kubernetes Cluster                        │
│                                                               │
│  ┌──────────────┐      ┌──────────────┐                     │
│  │   Pod: App   │─────▶│  Filebeat    │                     │
│  │  (Generates  │  Log │  (Collects   │                     │
│  │   Logs)      │ File │   Logs)      │                     │
│  └──────────────┘      └──────┬───────┘                     │
│                               │                              │
│                               ▼                              │
│                      ┌─────────────────┐                     │
│                      │   Logstash      │                     │
│                      │  (Processes &   │                     │
│                      │   Transforms)   │                     │
│                      └──────┬──────────┘                     │
│                             │                                │
│                             ▼                                │
│                    ┌──────────────────┐                      │
│                    │ Elasticsearch    │                      │
│                    │  (Stores Data)   │                      │
│                    └──────┬───────────┘                      │
│                           │                                  │
│                           ▼                                  │
│                    ┌──────────────────┐                      │
│                    │     Kibana       │                      │
│                    │  (Visualizes)    │                      │
│                    └──────────────────┘                      │
└─────────────────────────────────────────────────────────────┘
```

---

## Troubleshooting

### Common Issues and Solutions

#### 1. Pods Not Starting

**Problem:** Pods stuck in `Pending` or `Error` state

**Solutions:**
```bash
# Check pod events
kubectl describe pod <pod-name>

# Check pod logs
kubectl logs <pod-name>

# Check if there are resource constraints
kubectl describe nodes
```

#### 2. Elasticsearch Not Accessible

**Problem:** Can't access Elasticsearch at the NodePort

**Solutions:**
```bash
# Verify the service is running
kubectl get svc es-service

# Check if Elasticsearch is ready
kubectl get pods | grep es-logging

# Test connectivity from within cluster
kubectl run curl-test --image=curlimages/curl -it --rm -- curl http://es-service:9200
```

#### 3. Kibana Can't Connect to Elasticsearch

**Problem:** Kibana shows "Unable to connect to Elasticsearch"

**Solutions:**
```bash
# Verify the environment variable is set
kubectl get deployment kibana-logging -o yaml | grep ELASTICSEARCH_HOSTS

# Update the environment variable with correct IP
kubectl set env deployments/kibana-logging ELASTICSEARCH_HOSTS=http://192.168.49.2:31870

# Restart the deployment
kubectl rollout restart deployment kibana-logging
```

#### 4. No Logs in Kibana

**Problem:** Can't see logs in Kibana Discover

**Solutions:**
- Verify Filebeat is collecting logs:
```bash
kubectl logs -l app=logging-app-manual
```

- Check Logstash is processing:
```bash
kubectl logs -l app=logstash-logging
```

- Verify indices exist in Elasticsearch:
```bash
curl http://192.168.49.2:31870/_cat/indices?v
```

#### 5. ConfigMap Not Loading

**Problem:** Configuration changes not reflected

**Solutions:**
```bash
# Delete and recreate the ConfigMap
kubectl delete configmap <configmap-name>
kubectl create configmap <configmap-name> --from-file <config-file>

# Restart the deployment to pick up changes
kubectl rollout restart deployment <deployment-name>
```

---

## Commands Reference

### Useful Commands

```bash
# View all pods
kubectl get pods

# View all services
kubectl get svc

# View all deployments
kubectl get deploy

# View ConfigMaps
kubectl get cm

# View pod details
kubectl describe pod <pod-name>

# View pod logs
kubectl logs <pod-name>

# Get service URL
minikube service <service-name> --url

# Get minikube IP
minikube ip

# Scale deployment
kubectl scale deployment <deployment-name> --replicas=2

# Delete resources
kubectl delete -f <file-name>
```

---

## Next Steps

1. **Explore Kibana Features:**
   - Create visualizations
   - Build dashboards
   - Set up alerts

2. **Experiment with Filters:**
   - Modify Logstash filters
   - Add new data transformations
   - Parse additional log formats

3. **Expand Log Sources:**
   - Add more applications
   - Monitor different log paths
   - Integrate with other Beats

4. **Production Considerations:**
   - Implement persistent storage
   - Set up authentication
   - Configure resource limits
   - Enable monitoring

---

## Summary

In this lab, you have:

✅ Deployed Elasticsearch for log storage  
✅ Deployed Kibana for log visualization  
✅ Deployed Logstash for log processing  
✅ Configured Filebeat for log collection  
✅ Created and used Kubernetes ConfigMaps  
✅ Exposed services using NodePort  
✅ Verified the complete log pipeline  

The ELK Stack is now running on your Kubernetes cluster and ready to collect, process, and visualize logs!

---

## Additional Resources

- [Elasticsearch Documentation](https://www.elastic.co/guide/en/elasticsearch/reference/current/index.html)
- [Kibana User Guide](https://www.elastic.co/guide/en/kibana/current/index.html)
- [Logstash Documentation](https://www.elastic.co/guide/en/logstash/current/index.html)
- [Filebeat Documentation](https://www.elastic.co/guide/en/beats/filebeat/current/index.html)
- [Kubernetes Documentation](https://kubernetes.io/docs/home/)
- [Minikube Documentation](https://minikube.sigs.k8s.io/docs/)

---

**Happy Learning! 🚀**
