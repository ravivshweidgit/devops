# Prometheus Monitoring Stack - Student Guide

## Overview

This lesson covers the installation and configuration of the Prometheus monitoring stack on Kubernetes using Helm. The kube-prometheus-stack includes Prometheus, Grafana, Alertmanager, and various exporters for comprehensive Kubernetes monitoring.

## Prerequisites

- Kubernetes cluster running
- Helm 3.x installed
- kubectl configured to access your cluster
- Basic understanding of Kubernetes concepts

## Installation Steps

### 1. Add Prometheus Community Helm Repository

```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
```

### 2. Update Helm Repositories

```bash
helm repo update
```

### 3. Install kube-prometheus-stack

```bash
helm install kube-prometheus-stack \
  --create-namespace \
  --namespace kube-prometheus-stack \
  prometheus-community/kube-prometheus-stack
```

This command will:
- Create a new namespace called `kube-prometheus-stack`
- Install all Prometheus stack components in that namespace

## Verification

### Check Pod Status

After installation, verify all pods are running:

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

Expected services:
- `kube-prometheus-stack-alertmanager` (port 9093)
- `kube-prometheus-stack-grafana` (port 80)
- `kube-prometheus-stack-kube-state-metrics` (port 8080)
- `kube-prometheus-stack-operator` (port 443)
- `kube-prometheus-stack-prometheus` (port 9090)
- `kube-prometheus-stack-prometheus-node-exporter` (port 9100)

## Accessing Prometheus

### Port Forward to Prometheus

```bash
kubectl port-forward -n kube-prometheus-stack svc/kube-prometheus-stack-prometheus 9090:9090
```

**Note:** Use the service name with `svc/` prefix, not the pod name.

### Access Prometheus UI

Open your browser and navigate to:
```
http://localhost:9090/
```

## Prometheus Queries

### Basic Queries to Try

1. **Node CPU Metrics**
   ```
   node_cpu_seconds_total
   ```

2. **Pod Status Query**
   ```
   sum(kube_pod_status_phase{phase="Unknown"}) by (namespace, pod) or (count(kube_pod_deletion_timestamp) by (namespace, pod) * sum(kube_pod_status_reason{reason="NodeLost"}) by(namespace, pod))
   ```

3. **Service Creation Metrics**
   ```
   kube_service_created
   ```

4. **Deployment Replicas**
   ```
   kube_deployment_status_replicas_available
   ```

### Useful Resources

- [Kube State Metrics Documentation](https://github.com/kubernetes/kube-state-metrics/tree/main/docs)
- [Service Metrics](https://github.com/kubernetes/kube-state-metrics/blob/main/docs/metrics/service/service-metrics.md)
- [Deployment Metrics](https://github.com/kubernetes/kube-state-metrics/blob/main/docs/metrics/workload/deployment-metrics.md)

## Prometheus Configuration

### View Configuration via UI

Access the configuration at:
```
http://localhost:9090/config
```

### View Configuration in Cluster

```bash
kubectl exec -it prometheus-kube-prometheus-stack-prometheus-0 -n kube-prometheus-stack -- /bin/sh
```

Inside the pod:
```bash
cd /etc/prometheus/config_out
less prometheus.env.yaml
```

## Accessing Grafana

### Port Forward to Grafana

```bash
kubectl port-forward -n kube-prometheus-stack svc/kube-prometheus-stack-grafana 8080:80
```

### Get Grafana Credentials

```bash
kubectl get secret kube-prometheus-stack-grafana -n kube-prometheus-stack -o yaml
```

Decode the credentials:
```bash
echo "YWRtaW4=" | base64 -d  # Username: admin
echo "cHJvbS1vcGVyYXRvcg==" | base64 -d  # Password: prom-operator
```

### Access Grafana UI

Open your browser and navigate to:
```
http://localhost:8080/
```

**Login Credentials:**
- Username: `admin`
- Password: `prom-operator`

## Importing Grafana Dashboards

### Import Prometheus Dashboard

1. Navigate to: `http://localhost:8080/dashboards`
2. Click "Import"
3. Use Dashboard ID: `19268`
4. Or use the direct link: [Prometheus Dashboard](https://grafana.com/grafana/dashboards/19268-prometheus/)

## Architecture Overview

The kube-prometheus-stack includes:

- **Prometheus**: Time-series database and monitoring system
- **Grafana**: Visualization and dashboard platform
- **Alertmanager**: Alert routing and notification system
- **kube-state-metrics**: Exposes Kubernetes object state as metrics
- **node-exporter**: Exposes hardware and OS metrics
- **prometheus-operator**: Manages Prometheus and Alertmanager instances

## Troubleshooting

### Common Issues

1. **Port Forward Error**: Make sure to use `svc/` prefix when port-forwarding to services
2. **Pod Not Found**: Check if pods are in Running state
3. **Service Port Mismatch**: Verify service ports match your port-forward command

### Useful Commands

```bash
# Check all resources in the namespace
kubectl get all -n kube-prometheus-stack

# Check logs for specific components
kubectl logs -n kube-prometheus-stack prometheus-kube-prometheus-stack-prometheus-0

# Describe services for port information
kubectl describe svc kube-prometheus-stack-prometheus -n kube-prometheus-stack
```

## Next Steps

1. Explore the Prometheus query language (PromQL)
2. Create custom Grafana dashboards
3. Configure alerting rules
4. Set up notification channels in Alertmanager
5. Monitor application-specific metrics

## Cleanup

To remove the Prometheus stack:

```bash
helm uninstall kube-prometheus-stack -n kube-prometheus-stack
kubectl delete namespace kube-prometheus-stack
```

---

**Note**: This guide assumes you have a working Kubernetes cluster. Adjust commands as needed for your specific environment.
