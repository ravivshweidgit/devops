# Victoria Metrics Kubernetes Stack - Student Guide

## Overview

This guide will walk you through installing and exploring the Victoria Metrics Kubernetes Stack on a local minikube cluster. Victoria Metrics is a fast, cost-effective, and scalable open-source monitoring solution and time-series database.

## Prerequisites

Before starting, ensure you have the following installed:
- **minikube** - Local Kubernetes cluster
- **kubectl** - Kubernetes command-line tool
- **helm** - Kubernetes package manager

---

## Step 1: Environment Setup

### Delete Existing Minikube Cluster

Start with a clean slate by deleting any existing minikube cluster:

```bash
minikube delete
```

### Start Fresh Minikube Cluster

Initialize and start a new minikube cluster:

```bash
minikube start
```

This will create a new local Kubernetes cluster with default settings.

---

## Step 2: Install Victoria Metrics

### 1. Add the Victoria Metrics Helm Repository

Add the official Victoria Metrics Helm charts repository:

```bash
helm repo add vm https://victoriametrics.github.io/helm-charts/
```

You should see the output:
```
"vm" has been added to your repositories
```

### 2. Update Helm Repositories

Fetch the latest chart information:

```bash
helm repo update
```

### 3. Create Monitoring Namespace

Create a dedicated namespace for monitoring components:

```bash
kubectl create namespace monitoring
```

### 4. Install Victoria Metrics Kubernetes Stack

Install the complete Victoria Metrics stack using Helm:

```bash
helm install vm-stack vm/victoria-metrics-k8s-stack -n monitoring
```

This command will deploy all necessary components of the Victoria Metrics stack.

---

## Step 3: Verify Installation

### Check Pod Status

Verify that all pods are running correctly:

```bash
kubectl get pods -n monitoring
```

**Expected Output:**
```
NAME                                                            READY   STATUS    RESTARTS   AGE
vm-stack-grafana-fd49b998b-668tg                                1/2     Running   0          73s
vm-stack-kube-state-metrics-6458866c94-889hf                    1/1     Running   0          73s
vm-stack-prometheus-node-exporter-bt88n                         1/1     Running   0          73s
vm-stack-victoria-metrics-operator-86675f6fb7-mgbhp             1/1     Running   0          73s
vmagent-vm-stack-victoria-metrics-k8s-stack-c94644cf-cd4n2      2/2     Running   0          43s
vmalert-vm-stack-victoria-metrics-k8s-stack-b95786dd4-btxn7     2/2     Running   0          118s
vmalertmanager-vm-stack-victoria-metrics-k8s-stack-0            2/2     Running   0          2m58s
vmsingle-vm-stack-victoria-metrics-k8s-stack-7b5bb8bc67-5h9vp   1/1     Running   0          25s
```

**Key Components:**
- **vm-stack-grafana**: Web-based visualization and dashboards
- **vm-stack-kube-state-metrics**: Exposes Kubernetes cluster metrics
- **vm-stack-prometheus-node-exporter**: Collects system-level metrics
- **vm-stack-victoria-metrics-operator**: Manages Victoria Metrics resources
- **vmagent**: Metrics collection agent
- **vmalert**: Alert management
- **vmalertmanager**: Alert manager
- **vmsingle**: Single-node Victoria Metrics instance

### View All Resources

To see a complete overview of all resources:

```bash
kubectl get all -A
```

---

## Step 4: Access Grafana Dashboard

### 1. Retrieve Grafana Admin Password

Get the Grafana admin password from the Kubernetes secret:

```bash
kubectl get secret -n monitoring vm-stack-grafana -o jsonpath="{.data.admin-password}" | base64 --decode ; echo
```

**Note:** Save this password, you'll need it to log in to Grafana.

Example output:
```
1rpO3pFD4ST8yHuk7z8DKFH5mGxyRlDzKKO3uEmE
```

### 2. Port Forward to Access Grafana

Create a port forward to access Grafana locally:

```bash
kubectl port-forward deployment/vm-stack-grafana 3000:3000 -n monitoring
```

The output should show:
```
Forwarding from 127.0.0.1:3000 -> 3000
Forwarding from [::1]:3000 -> 3000
```

### 3. Access Grafana in Browser

Open your web browser and navigate to:

```
http://localhost:3000
```

### 4. Login to Grafana

Use the following credentials:
- **Username:** `admin`
- **Password:** (the password you retrieved in step 1)

---

## Step 5: Explore Victoria Metrics

### Pre-configured Dashboards

Once logged into Grafana, you'll find several pre-configured dashboards:

1. **Home Dashboards VictoriaMetrics - operator**
   - Monitor the Victoria Metrics operator status and performance

2. **Home Dashboards VictoriaMetrics - vmagent**
   - Monitor the metrics collection agent (vmagent) status

### Run Example Queries

Navigate to **Explore** in Grafana to run custom queries:

#### Access Query Interface

1. Click on **Home** → **Explore**
2. Select **VictoriaMetrics** as the data source

#### Sample Queries

Try these example queries to get familiar with Victoria Metrics:

**Query 1: View VM Blocks**
```promql
vm_blocks_ru
```

This query shows the resource usage of Victoria Metrics blocks.

**Query 2: Application Start Timestamp**
```promql
vm_app_start_timestamp
```

This query displays when the Victoria Metrics application started.

---

## Architecture Overview

### What is Victoria Metrics?

Victoria Metrics is a fast, cost-effective, and scalable monitoring solution and time-series database. Key benefits:

- **High Performance**: 20x faster than Prometheus
- **Cost Efficient**: 7x better data compression
- **Scalable**: Supports millions of metrics
- **Drop-in Replacement**: Compatible with Prometheus query API

### Component Roles

1. **VMSingle**: Single-node Victoria Metrics instance that stores and queries time-series data
2. **VMAgent**: Lightweight metrics collection agent that scrapes metrics and forwards them to VMSingle
3. **VMO Operator**: Kubernetes operator that manages Victoria Metrics resources
4. **Grafana**: Visualization layer for creating dashboards and graphs
5. **VMAlert**: Rule-based alerting system
6. **VMAlertmanager**: Handles alert routing and grouping
7. **Kube State Metrics**: Exposes Kubernetes cluster state metrics
8. **Node Exporter**: Collects system-level metrics from nodes

---

## Troubleshooting

### Pods Not Running

If pods are stuck in `Pending` or `CrashLoopBackOff`:

```bash
# Check pod logs
kubectl logs <pod-name> -n monitoring

# Describe pod for events
kubectl describe pod <pod-name> -n monitoring
```

### Port Forward Issues

If port forwarding fails:

```bash
# Check if Grafana pod is running
kubectl get pods -n monitoring | grep grafana

# Try deleting and recreating the port forward
# Press Ctrl+C to stop the port forward, then run it again
```

### Access Issues

If you can't access Grafana:

1. Verify the port forward is still active
2. Check if the Grafana pod is in `Running` state (2/2 ready)
3. Try retrieving the password again if login fails

---

## Next Steps

1. **Create Custom Dashboards**: Build your own dashboards in Grafana
2. **Configure Alerts**: Set up alerting rules with VMAlert
3. **Explore More Queries**: Experiment with PromQL queries
4. **Monitor Your Applications**: Integrate your applications with vmagent
5. **Learn PromQL**: Deep dive into Prometheus Query Language

---

## Cleanup

To remove the Victoria Metrics stack:

```bash
# Uninstall the Helm release
helm uninstall vm-stack -n monitoring

# Delete the namespace
kubectl delete namespace monitoring

# Optional: Delete the entire minikube cluster
minikube delete
```

---

## Additional Resources

- [Victoria Metrics Official Documentation](https://docs.victoriametrics.com/)
- [Grafana Documentation](https://grafana.com/docs/)
- [PromQL Guide](https://prometheus.io/docs/prometheus/latest/querying/basics/)
- [Victoria Metrics Helm Charts](https://github.com/VictoriaMetrics/helm-charts)

---

## Summary

In this guide, you successfully:

✅ Set up a fresh minikube cluster  
✅ Added Victoria Metrics Helm repository  
✅ Installed the complete Victoria Metrics Kubernetes Stack  
✅ Verified all components are running  
✅ Accessed Grafana dashboard  
✅ Explored pre-configured dashboards  
✅ Executed sample PromQL queries  

Congratulations! You now have a fully functional Victoria Metrics monitoring stack running on your local Kubernetes cluster.
