# ArgoCD Advanced Patterns - Student Guide

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Previous Lesson Recap](#previous-lesson-recap)
3. [ApplicationSet with Git Generator](#applicationset-with-git-generator)
4. [App-of-Apps Pattern](#app-of-apps-pattern)
5. [Best Practices](#best-practices)
6. [Cleanup Procedures](#cleanup-procedures)

---

## Prerequisites

Before starting this lesson, ensure you have:
- Minikube running
- kubectl configured
- Basic understanding of Kubernetes
- ArgoCD installed and accessible

---

## Previous Lesson Recap

In the previous lesson, we successfully:
1. Started Minikube
2. Created the ArgoCD namespace
3. Installed ArgoCD using the official manifests
4. Retrieved the admin password
5. Accessed the ArgoCD UI

### Key Commands from Previous Lesson:
```bash
# Start Minikube
minikube start

# Create ArgoCD namespace
kubectl create ns argocd

# Install ArgoCD
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

# Get admin password
kubectl -n argocd get secret argocd-initial-admin-secret -o yaml
echo "TzZjM3dZeDNBc0prVVdKeQ==" | base64 -d

# Port forward to access UI
kubectl -n argocd port-forward svc/argocd-server 8080:443
```

**ArgoCD UI Access:**
- URL: https://localhost:8080/applications
- Username: admin
- Password: O6c3wYx3AsJkUWJy

---

## ApplicationSet with Git Generator

### Overview
ApplicationSet is a powerful ArgoCD feature that allows you to manage multiple applications using generators. The Git generator automatically discovers applications based on directory structure in a Git repository.

### Example 1: Security Policy Charts

We'll create an ApplicationSet that automatically deploys security policy charts from a Git repository.

#### Step 1: Create the ApplicationSet Manifest

Create a file called `application-set.yaml`:

```yaml
apiVersion: argoproj.io/v1alpha1
kind: ApplicationSet
metadata:
  name: cluster-addons
  namespace: argocd
spec:
  generators:
  - git:
      repoURL: https://github.com/mabusaa/argocd-example-apps.git
      revision: HEAD
      directories:
      - path: helmcharts/security-policy-charts/*
              
  template:
    metadata:
      name: '{{path.basename}}'
      namespace: argocd
    spec:
      project: default
      source:
        repoURL: https://github.com/mabusaa/argocd-example-apps.git
        targetRevision: HEAD
        path: '{{path}}'
        helm:
          releaseName: '{{path.basename}}'
      destination:
        server: https://kubernetes.default.svc
        namespace: '{{path.basename}}'
      syncPolicy:
        syncOptions:
        - CreateNamespace=true
```

#### Step 2: Apply the ApplicationSet

```bash
kubectl apply -f application-set.yaml
```

Expected output:
```
applicationset.argoproj.io/cluster-addons created
```

#### Step 3: Verify Applications Created

1. Open ArgoCD UI: https://localhost:8080/applications
2. You should see two applications created:
   - **falco** - Runtime security monitoring
   - **kyverno** - Policy engine for Kubernetes

#### Step 4: Sync Applications

1. In the ArgoCD UI, select each application
2. Click the "SYNC" button
3. Monitor the deployment status

#### Step 5: Cleanup

```bash
kubectl delete -f application-set.yaml
```

Expected output:
```
applicationset.argoproj.io "cluster-addons" deleted from argocd namespace
```

### Understanding the ApplicationSet Configuration

| Field | Description |
|-------|-------------|
| `generators.git.repoURL` | Source Git repository URL |
| `generators.git.directories.path` | Directory pattern to scan for applications |
| `template.metadata.name` | Application name template using `{{path.basename}}` |
| `template.spec.source.path` | Path to application manifests |
| `template.spec.destination.namespace` | Target namespace for deployment |
| `syncOptions.CreateNamespace` | Automatically create namespace if it doesn't exist |

---

## App-of-Apps Pattern

The App-of-Apps pattern is a powerful approach for managing multiple applications as a single unit. We'll explore two variations.

### Prerequisites

Clone the example repository:
```bash
cd ~/projects
git clone https://github.com/mabusaa/argocd-course-app-of-apps.git
cd argocd-course-app-of-apps
```

### Example 2: Root App Directory Approach

This approach uses a root application that points to a directory containing multiple application manifests.

#### Step 1: Apply the Root Application

```bash
kubectl apply -f root-app-directory-approach.yaml
```

Expected output:
```
application.argoproj.io/root-app-directory-approach created
```

#### Step 2: Sync Applications

1. Go to ArgoCD UI
2. Find the "root-app-directory-approach" application
3. Click "SYNC" to deploy all child applications

#### Step 3: Cleanup

```bash
kubectl delete -f root-app-directory-approach.yaml
```

### Example 3: Root App Helm Approach

This approach uses Helm charts to manage multiple applications with automatic synchronization.

#### Step 1: Apply the Root Application

```bash
kubectl apply -f root-app-helm-approach.yaml
```

Expected output:
```
application.argoproj.io/root-app-helm-approach created
```

**Note:** This example includes auto-sync, so applications will be deployed automatically.

#### Step 2: Monitor Deployment

1. Go to ArgoCD UI
2. Observe the automatic deployment of child applications
3. Applications should sync automatically without manual intervention

#### Step 3: Cleanup

```bash
kubectl delete -f root-app-helm-approach.yaml
```

---

## Best Practices

### 1. ApplicationSet Best Practices
- Use meaningful names for ApplicationSets
- Leverage Git generators for dynamic application discovery
- Use templating for consistent naming conventions
- Include `CreateNamespace=true` for automatic namespace creation

### 2. App-of-Apps Best Practices
- Use root applications to manage related applications
- Consider auto-sync for development environments
- Use manual sync for production environments
- Implement proper RBAC for different environments

### 3. Security Considerations
- Use private repositories when possible
- Implement proper RBAC policies
- Regularly rotate admin passwords
- Monitor application deployments

### 4. Monitoring and Troubleshooting
- Check ArgoCD UI for application status
- Use `kubectl get applications -n argocd` to list applications
- Monitor pod logs for troubleshooting
- Use ArgoCD CLI for advanced operations

---

## Cleanup Procedures

### Complete Environment Cleanup

To completely clean up the ArgoCD environment:

```bash
# Delete all applications
kubectl delete applications --all -n argocd

# Delete all application sets
kubectl delete applicationsets --all -n argocd

# Delete ArgoCD installation
kubectl delete -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

# Delete namespace
kubectl delete ns argocd

# Stop Minikube
minikube stop
```

### Individual Resource Cleanup

```bash
# Delete specific ApplicationSet
kubectl delete applicationset <name> -n argocd

# Delete specific Application
kubectl delete application <name> -n argocd

# Delete all resources in a namespace
kubectl delete all --all -n <namespace>
```

---

## Key Takeaways

1. **ApplicationSet** provides powerful automation for managing multiple applications
2. **Git Generator** enables dynamic application discovery based on repository structure
3. **App-of-Apps pattern** allows hierarchical application management
4. **Auto-sync** can be useful for development but should be used carefully in production
5. **Proper cleanup** is essential to avoid resource conflicts

---

## Next Steps

After completing this lesson, consider:
1. Exploring other ApplicationSet generators (Cluster, List, etc.)
2. Implementing ArgoCD in a multi-cluster environment
3. Setting up proper RBAC and security policies
4. Integrating ArgoCD with CI/CD pipelines
5. Exploring ArgoCD plugins and extensions

---

## Troubleshooting

### Common Issues

1. **Applications not appearing**: Check ApplicationSet configuration and Git repository access
2. **Sync failures**: Verify target cluster connectivity and permissions
3. **Namespace issues**: Ensure `CreateNamespace=true` is set or namespaces exist
4. **Authentication problems**: Verify ArgoCD admin credentials and RBAC settings

### Useful Commands

```bash
# Check ArgoCD pods
kubectl get pods -n argocd

# Check applications
kubectl get applications -n argocd

# Check application sets
kubectl get applicationsets -n argocd

# Describe application for details
kubectl describe application <name> -n argocd
```

---

*This guide covers the essential concepts and practical examples for working with ArgoCD ApplicationSets and App-of-Apps patterns. Practice these examples and experiment with different configurations to deepen your understanding.*
