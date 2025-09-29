# ArgoCD YAML-Based Deployment - Student Guide

## Overview
This guide demonstrates how to deploy and manage ArgoCD applications using **YAML files** instead of the ArgoCD UI or CLI. We'll learn the declarative approach to ArgoCD management, including projects, repository secrets, and applications - all defined as YAML manifests.

## Learning Objectives
By the end of this lesson, you will understand:
- How to define ArgoCD **Projects** using YAML
- How to configure **Repository Secrets** using YAML
- How to create **Applications** using YAML manifests
- The declarative approach to ArgoCD management
- YAML-based GitOps workflow

## Prerequisites
- Minikube or Kubernetes cluster
- kubectl configured
- Basic understanding of ArgoCD (previous lesson covered UI/CLI approach)
- SSH key pair for GitHub authentication
- Private GitHub repository

## Step 1: Start Minikube and Create ArgoCD Namespace

```bash
minikube start
kubectl create ns argocd
```

## Step 2: Install ArgoCD

```bash
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
```

Verify the installation:
```bash
kubectl get po -n argocd
```

Expected output:
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

## Step 3: Access ArgoCD UI

### Get Admin Password
```bash
kubectl -n argocd get secret argocd-initial-admin-secret -o yaml
```

Decode the password:
```bash
echo "TzZjM3dZeDNBc0prVVdKeQ==" | base64 -d
```

### Port Forward to Access UI
```bash
kubectl -n argocd port-forward svc/argocd-server 8080:443
```

Access the UI at: https://localhost:8080/applications
- Username: `admin`
- Password: `O6c3wYx3AsJkUWJy` (or your decoded password)

## Step 4: Create Private Repository

1. Fork the repository: https://github.com/argoproj/argocd-example-apps
2. Create your own private repository: https://github.com/ravivshweidgit/argocd-example-apps

## Step 5: YAML-Based ArgoCD Project Definition

**Key Learning Point**: Instead of creating projects through the UI, we define them as YAML manifests.

Create `my-argocd-proj.yaml`:

```yaml
apiVersion: argoproj.io/v1alpha1
kind: AppProject
metadata:
  name: my-project
  namespace: argocd
  # Finalizer that ensures that project is not deleted until it is not referenced by any application
  finalizers:
    - resources-finalizer.argocd.argoproj.io
spec:
  description: Example Project
  # Allow manifests to deploy from any Git repos
  sourceRepos:
  - '*'
  # Only permit applications to deploy to the guestbook namespace in the same cluster
  destinations:
  - namespace: argocd
    server: https://kubernetes.default.svc
  # Deny all cluster-scoped resources from being created, except for Namespace
  clusterResourceWhitelist:
  - group: '*'
    kind: '*'
```

Apply the project using kubectl:
```bash
kubectl apply -f my-argocd-proj.yaml
```

**YAML Benefits**: 
- Version controlled project definitions
- Reproducible deployments
- Infrastructure as Code approach

## Step 6: YAML-Based Repository Secret Configuration

**Key Learning Point**: Repository authentication is also defined as YAML, not configured through UI.

### Identify Your SSH Key
First, check which SSH key you're using with GitHub:
```bash
ssh -T git@github.com
```

Check your SSH keys:
```bash
ls -la ~/.ssh/
ssh-add -l
```

### Create SSH Secret
Create `ssh.yaml` with the correct SSH key:

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: private-repo
  namespace: argocd
  labels:
    argocd.argoproj.io/secret-type: repository
stringData:
  type: git
  url: git@github.com:ravivshweidgit/argocd-example-apps.git
  sshPrivateKey: |
    # REPLACE WITH YOUR ACTUAL SSH PRIVATE KEY
    # DO NOT COMMIT REAL PRIVATE KEYS TO GIT!
    # Example format:
    # -----BEGIN OPENSSH PRIVATE KEY-----
    # your-private-key-content-here
    # -----END OPENSSH PRIVATE KEY-----
```

**Important Security Notes:**
- Replace the `url` with your actual repository URL
- Replace the `sshPrivateKey` with your actual SSH private key content
- The key should be in the original format, NOT base64 encoded
- Make sure you're using the correct key type (ED25519 vs RSA)
- **⚠️ NEVER commit real private keys to Git repositories!**
- Use placeholder text in version-controlled files
- Apply real keys only in your local environment or secure CI/CD systems

Apply the SSH secret using kubectl:
```bash
kubectl apply -f ssh.yaml
```

**YAML Benefits**:
- Declarative repository configuration
- No manual UI configuration needed
- Consistent across environments

## Step 7: YAML-Based Application Definition

**Key Learning Point**: Applications are defined as YAML manifests, enabling GitOps workflows.

Create `application.yaml`:

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
```

Apply the application using kubectl:
```bash
kubectl apply -f application.yaml
```

**YAML Benefits**:
- Complete application definition in code
- GitOps-ready configuration
- Easy to version control and review
- Reproducible deployments

## Step 8: YAML vs UI/CLI Comparison

| Aspect | UI/CLI Approach | YAML Approach |
|--------|----------------|---------------|
| **Configuration** | Manual clicks/commands | Declarative files |
| **Version Control** | Not tracked | Fully tracked in Git |
| **Reproducibility** | Manual recreation | Automated via kubectl |
| **Review Process** | No code review | Full code review |
| **GitOps** | Not suitable | Perfect fit |
| **Environment Consistency** | Error-prone | Guaranteed |

## Step 9: Troubleshooting Common Issues

### Issue: "SSH agent requested but SSH_AUTH_SOCK not-specified"

**Root Cause:** This error typically occurs when:
1. The SSH private key is base64 encoded instead of being in its original format
2. The wrong SSH key type is being used (e.g., RSA instead of ED25519)
3. The SSH key doesn't match the one configured in GitHub

**Solution:**
1. Verify which SSH key you're using with GitHub:
   ```bash
   ssh -vT git@github.com
   ```
2. Use the correct SSH key in your `ssh.yaml` file
3. Ensure the key is in its original format, not base64 encoded
4. Restart the ArgoCD repo server after making changes:
   ```bash
   kubectl rollout restart deployment/argocd-repo-server -n argocd
   ```

### Issue: Application shows "OutOfSync" status

**Solution:** Sync the application:
```bash
kubectl patch application guestbook -n argocd --type merge -p '{"operation":{"sync":{"syncOptions":["CreateNamespace=true"]}}}'
```

## Step 10: Verify YAML-Based Deployment

Check application status:
```bash
kubectl get application guestbook -n argocd
```

Check deployed resources:
```bash
kubectl get pods -n argocd | grep guestbook
kubectl get svc -n argocd | grep guestbook
```

Expected output:
```
NAME        SYNC STATUS   HEALTH STATUS
guestbook   Synced        Progressing

NAME                                        READY   STATUS    RESTARTS   AGE
guestbook-helm-guestbook-6585c766d6-fqbcq   1/1     Running   0          47s

NAME                        TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)   AGE
guestbook-helm-guestbook    ClusterIP   10.107.135.101   <none>        80/TCP    55s
```

## Key Takeaways

### YAML-Based ArgoCD Management
1. **Declarative Approach**: All ArgoCD resources (Projects, Secrets, Applications) are defined as YAML
2. **Version Control**: YAML files can be version controlled in Git for full traceability
3. **GitOps Ready**: YAML approach enables true GitOps workflows
4. **Reproducibility**: Environments can be recreated consistently using the same YAML files
5. **Code Review**: Changes go through proper code review processes

### YAML File Structure
- **Projects** (`my-argocd-proj.yaml`): Define permissions and constraints
- **Repository Secrets** (`ssh.yaml`): Configure Git repository access
- **Applications** (`application.yaml`): Define what to deploy and where

### Benefits Over UI/CLI
- **Infrastructure as Code**: Everything is defined in code
- **Automation**: Can be automated with CI/CD pipelines
- **Consistency**: Same configuration across all environments
- **Audit Trail**: Full history of changes in Git

## Security Best Practices

### ⚠️ Private Key Security
- **Never commit private keys to Git repositories**
- Use placeholder text in version-controlled files
- Apply real keys only in secure environments
- Consider using Kubernetes secrets management tools
- Use CI/CD systems with secure secret injection

### Safe Git Workflow
1. Create template files with placeholder keys
2. Commit template files to Git
3. Apply real keys locally or in secure CI/CD
4. Never push actual private keys to remote repositories

## Next Steps

- **Advanced YAML Features**: Explore sync policies, health checks, and resource hooks in YAML
- **Application Sets**: Learn to manage multiple applications with YAML-based ApplicationSets
- **GitOps Workflows**: Set up automated deployments triggered by Git commits
- **YAML Templating**: Use tools like Helm or Kustomize with ArgoCD YAML definitions
- **Multi-Environment**: Create environment-specific YAML configurations

## Additional Resources

- [ArgoCD Documentation](https://argo-cd.readthedocs.io/)
- [ArgoCD SSH Repository Configuration](https://argo-cd.readthedocs.io/en/stable/operator-manual/declarative-setup/#repositories)
- [GitHub SSH Key Setup](https://docs.github.com/en/authentication/connecting-to-github-with-ssh)
