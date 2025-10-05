# ArgoCD Advanced Sync Features - Student Guide

## Overview
This lesson builds upon the previous ArgoCD YAML-based deployment lesson and focuses on **advanced sync policies and features**. We'll explore automated sync, pruning, self-healing, target revisions, and sync waves to demonstrate how ArgoCD maintains desired state and handles complex deployment scenarios.

## Learning Objectives
By the end of this lesson, you will understand:
- How to configure **automated sync policies**
- The concept of **pruning** and when to use it
- **Self-healing** capabilities for drift correction
- **Target revisions** for rollback scenarios
- **Sync waves** for ordered deployments with hooks
- Advanced ArgoCD operational features

## Prerequisites
- Completed the previous ArgoCD YAML-based deployment lesson
- ArgoCD running with a working application
- Access to the source Git repository
- Basic understanding of Git and Kubernetes

## Lesson Context
This lesson continues from where we left off in the previous session, where we had:
- ArgoCD installed and configured
- A working guestbook application deployed via YAML
- Private repository access configured
- Basic application synchronization working

---

## Part 1: Automated Sync Policy

### Objective
Enable automatic synchronization when changes are detected in the source repository.

### Step 1: Configure Automated Sync

Edit your `application.yaml` to add automated sync policy:

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: guestbook
  namespace: argocd
spec:
  project: my-project
  source:
    repoURL: git@github.com:ravivshweidgit/argocd-example-apps.git
    targetRevision: HEAD
    path: helm-guestbook
  destination:
    server: https://kubernetes.default.svc
    namespace: argocd
  syncPolicy:
    automated: {}
```

Apply the changes:
```bash
kubectl apply -f application.yaml
```

### Step 2: Test Automated Sync

1. **Make a change** in your source repository:
   - Edit `helm-guestbook/values.yaml`
   - Change the service port from `80` to `8080`:
   ```yaml
   service:
     type: ClusterIP
     port: 8080
   ```

2. **Commit and push** the change:
   ```bash
   git add helm-guestbook/values.yaml
   git commit -m "port: 8080"
   git push
   ```

3. **Monitor the sync**:
   - Check ArgoCD UI: https://localhost:8080/applications
   - Or check via CLI:
   ```bash
   kubectl get application guestbook -n argocd
   kubectl get svc -n argocd | grep guestbook
   ```

**Expected Result**: ArgoCD automatically detects the change and syncs the application, updating the service port to 8080.

---

## Part 2: Pruning - Automatic Resource Cleanup

### Objective
Configure ArgoCD to automatically remove resources that are no longer defined in the source repository.

### Step 1: Enable Pruning

Update your `application.yaml` to include pruning:

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: guestbook
  namespace: argocd
spec:
  project: my-project
  source:
    repoURL: git@github.com:ravivshweidgit/argocd-example-apps.git
    targetRevision: HEAD
    path: helm-guestbook
  destination:
    server: https://kubernetes.default.svc
    namespace: argocd
  syncPolicy:
    automated:
      prune: true
```

Apply the changes:
```bash
kubectl apply -f application.yaml
```

### Step 2: Test Pruning

1. **Scale down to zero replicas**:
   - Edit `helm-guestbook/values.yaml`
   - Change replica count from `1` to `0`:
   ```yaml
   replicaCount: 0
   ```

2. **Commit and push**:
   ```bash
   git add helm-guestbook/values.yaml
   git commit -m "scale to zero replicas"
   git push
   ```

3. **Verify pruning**:
   ```bash
   kubectl get rs -n argocd
   kubectl get deploy -n argocd
   ```

**Expected Result**: The replica set scales down to 0 replicas, effectively removing the running pods.

---

## Part 3: Self-Healing - Drift Correction

### Objective
Configure ArgoCD to automatically correct manual changes made directly to Kubernetes resources.

### Step 1: Create Drift by Scaling Up

First, manually scale the deployment to create drift:

```bash
kubectl scale deployment guestbook-helm-guestbook --replicas=5 -n argocd
```

Verify the manual change:
```bash
kubectl get deploy -n argocd
```
You should see 5 replicas running.

### Step 2: Enable Self-Healing

Now update your `application.yaml` to include self-healing:

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: guestbook
  namespace: argocd
spec:
  project: my-project
  source:
    repoURL: git@github.com:ravivshweidgit/argocd-example-apps.git
    targetRevision: HEAD
    path: helm-guestbook
  destination:
    server: https://kubernetes.default.svc
    namespace: argocd
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
```

Apply the self-healing policy:
```bash
kubectl apply -f application.yaml
```

### Step 3: Observe Self-Healing

Wait for self-healing to take effect:
```bash
kubectl get deploy -n argocd
```

**Expected Result**: ArgoCD will detect the drift and automatically scale back to 0 replicas (as defined in the repository).

**Expected Result**: ArgoCD automatically corrects the manual scaling, reverting to the desired state defined in the repository.

---

## Part 4: Target Revision - Rollback Scenarios

### Objective
Configure ArgoCD to sync to a specific commit/revision instead of HEAD, enabling rollback capabilities.

### Step 1: Configure Target Revision

Update your `application.yaml` to use a specific target revision:

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: guestbook
  namespace: argocd
spec:
  project: my-project
  source:
    repoURL: git@github.com:ravivshweidgit/argocd-example-apps.git
    targetRevision: 3938f17f5e713020ed1ecc9381f0e75125426637  # Specific commit hash
    path: helm-guestbook
  destination:
    server: https://kubernetes.default.svc
    namespace: argocd
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
```

Apply the changes:
```bash
kubectl apply -f application.yaml
```

### Step 2: Verify Rollback

Check that the application reverts to the state at that specific commit:
```bash
kubectl get svc -n argocd | grep guestbook
```

**Expected Result**: The service port should revert to 80 (the original value before our changes).

---

## Part 5: Sync Waves - Ordered Deployments with Hooks

### Objective
Demonstrate how to create ordered deployments using sync waves and lifecycle hooks.

### Step 1: Create Sync Waves Application

Create `application-sync-waves.yaml`:

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: sync-waves
  namespace: argocd
spec:
  project: my-project
  source:
    repoURL: git@github.com:ravivshweidgit/argocd-example-apps.git
    targetRevision: HEAD
    path: sync-waves
  destination:
    server: https://kubernetes.default.svc
    namespace: argocd
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
```

Apply the application:
```bash
kubectl apply -f application-sync-waves.yaml
```

### Step 2: Monitor Sync Waves

The sync waves manifests already exist in the source repository at `sync-waves/manifests.yaml`. After applying the application, you can immediately monitor the deployment:

**Monitor the deployment** in ArgoCD UI:
- Go to: https://localhost:8080/applications/argocd/sync-waves?view=tree&resource=
- Watch the resources deploy in order according to their sync waves

The existing manifests include:

```yaml
---
apiVersion: batch/v1
kind: Job
metadata:
  generateName: upgrade-sql-schema
  annotations:
    argocd.argoproj.io/hook: PreSync
spec:
  template:
    spec:
      containers:
        - name: upgrade-sql-schema
          image: alpine:latest
          command: ["sleep", "5"]
      restartPolicy: Never
---
apiVersion: apps/v1
kind: ReplicaSet
metadata:
  name: backend
spec:
  replicas: 1
  selector:
    matchLabels:
      tier: backend
  template:
    metadata:
      labels:
        tier: backend
    spec:
      containers:
        - name: main
          image: nginx:latest
---
apiVersion: v1
kind: Service
metadata:
  name: backend
spec:
  selector:
    tier: backend
  ports:
    - protocol: TCP
      port: 8080
      targetPort: 8080
---
apiVersion: batch/v1
kind: Job
metadata:
  name: maint-page-up
  annotations:
    argocd.argoproj.io/hook: Sync
    argocd.argoproj.io/hook-delete-policy: BeforeHookCreation
    argocd.argoproj.io/sync-wave: "1"
spec:
  template:
    spec:
      containers:
        - name: page-up
          image: alpine:latest
          command: ["sleep", "2"]
      restartPolicy: Never
  backoffLimit: 0
---
apiVersion: apps/v1
kind: ReplicaSet
metadata:
  name: frontend
  annotations:
    argocd.argoproj.io/sync-wave: "2"
spec:
  replicas: 1
  selector:
    matchLabels:
      tier: frontend
  template:
    metadata:
      labels:
        tier: frontend
    spec:
      containers:
        - name: main
          image: nginx:latest
---
apiVersion: v1
kind: Service
metadata:
  name: frontend
  annotations:
    argocd.argoproj.io/sync-wave: "2"
spec:
  selector:
    tier: frontend
  ports:
    - protocol: TCP
      port: 80
      targetPort: 80
---
apiVersion: batch/v1
kind: Job
metadata:
  name: maint-page-down
  annotations:
    argocd.argoproj.io/hook: Sync
    argocd.argoproj.io/hook-delete-policy: BeforeHookCreation
    argocd.argoproj.io/sync-wave: "3"
spec:
  template:
    spec:
      containers:
        - name: page-down
          image: alpine:latest
          command: ["sleep", "2"]
      restartPolicy: Never
```

**Expected Execution Order**:
1. **PreSync Hook**: `upgrade-sql-schema` job runs first
2. **Wave 0** (default): Backend ReplicaSet and Service deploy
3. **Wave 1**: `maint-page-up` job runs
4. **Wave 2**: Frontend ReplicaSet and Service deploy
5. **Wave 3**: `maint-page-down` job runs

---

## Understanding Sync Features

### Sync Policy Options

| Feature | Purpose | Use Case |
|---------|---------|----------|
| `automated: {}` | Auto-sync on changes | Continuous deployment |
| `prune: true` | Remove deleted resources | Clean up old resources |
| `selfHeal: true` | Correct manual changes | Maintain desired state |
| `targetRevision` | Sync to specific commit | Rollbacks, testing |

### Sync Waves and Hooks

| Annotation | Purpose | Execution Order |
|------------|---------|-----------------|
| `argocd.argoproj.io/sync-wave: "N"` | Define deployment order | Lower numbers first |
| `argocd.argoproj.io/hook: PreSync` | Run before sync | Before all resources |
| `argocd.argoproj.io/hook: Sync` | Run during sync | In sync wave order |
| `argocd.argoproj.io/hook: PostSync` | Run after sync | After all resources |

### Hook Delete Policies

| Policy | Behavior |
|--------|----------|
| `BeforeHookCreation` | Delete previous hook before creating new one |
| `HookSucceeded` | Delete hook after successful completion |
| `HookFailed` | Delete hook after failure |

---

## Key Takeaways

### Advanced Sync Capabilities
1. **Automated Sync**: Enables continuous deployment without manual intervention
2. **Pruning**: Automatically removes resources no longer in source
3. **Self-Healing**: Corrects manual changes to maintain desired state
4. **Target Revisions**: Enables rollbacks to specific commits
5. **Sync Waves**: Provides ordered deployment with lifecycle hooks

### Operational Benefits
- **Reduced Manual Work**: Automated sync reduces operational overhead
- **Consistency**: Self-healing maintains desired state
- **Safety**: Pruning prevents resource drift
- **Flexibility**: Target revisions enable controlled rollbacks
- **Ordered Deployments**: Sync waves handle complex deployment scenarios

### Best Practices
- Use automated sync for development environments
- Enable pruning for clean resource management
- Use self-healing for production environments
- Test rollbacks using target revisions
- Use sync waves for complex multi-tier applications

---

## Next Steps

- **Advanced Hooks**: Explore more hook types (PostSync, Fail)
- **Sync Options**: Learn about sync options and resource filters
- **Application Sets**: Manage multiple applications with sync policies
- **Monitoring**: Set up alerts for sync failures and drift detection
- **Security**: Implement RBAC for sync policy management

---

## Troubleshooting

### Common Issues

1. **Sync Not Triggering**: Check if automated sync is enabled
2. **Resources Not Pruned**: Verify prune policy is set to true
3. **Self-Healing Not Working**: Ensure selfHeal is enabled and resources are managed by ArgoCD
4. **Sync Waves Not Ordered**: Check sync-wave annotations and wave numbers
5. **Hooks Failing**: Review hook logs and ensure proper image availability

### Useful Commands

```bash
# Check application sync status
kubectl get application -n argocd

# View sync policy
kubectl get application guestbook -n argocd -o yaml

# Monitor sync waves
kubectl get events -n argocd --sort-by='.lastTimestamp'

# Check hook jobs
kubectl get jobs -n argocd
```

---

## Additional Resources

- [ArgoCD Sync Policies Documentation](https://argo-cd.readthedocs.io/en/stable/user-guide/sync-policies/)
- [ArgoCD Hooks Documentation](https://argo-cd.readthedocs.io/en/stable/user-guide/hooks/)
- [ArgoCD Sync Waves Documentation](https://argo-cd.readthedocs.io/en/stable/user-guide/sync-waves/)
- [ArgoCD Best Practices](https://argo-cd.readthedocs.io/en/stable/operator-manual/security/)
