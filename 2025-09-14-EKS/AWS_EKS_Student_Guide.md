# AWS EKS (Elastic Kubernetes Service) - Student Guide

## Table of Contents
1. [Learning Objectives](#learning-objectives)
2. [Prerequisites](#prerequisites)
3. [Overview](#overview)
4. [Infrastructure Components](#infrastructure-components)
5. [Terraform Configuration](#terraform-configuration)
6. [Step-by-Step Implementation](#step-by-step-implementation)
7. [Verification and Testing](#verification-and-testing)
8. [Cleanup](#cleanup)
9. [Troubleshooting](#troubleshooting)
10. [Key Concepts Summary](#key-concepts-summary)

## Learning Objectives

By the end of this lesson, students will be able to:

- Understand AWS EKS architecture and components
- Deploy an EKS cluster using Terraform
- Configure VPC networking for EKS
- Set up managed node groups with auto-scaling
- Connect to and manage the EKS cluster using kubectl
- Understand security groups and IAM roles for EKS
- Clean up AWS resources properly

## Prerequisites

Before starting this lesson, ensure you have:

- AWS CLI configured with appropriate permissions
- Terraform installed (version ~> 1.3)
- kubectl installed
- Basic understanding of Kubernetes concepts
- Basic knowledge of Terraform
- AWS account with sufficient permissions for EKS, VPC, and EC2

## Overview

Amazon Elastic Kubernetes Service (EKS) is a managed Kubernetes service that makes it easy to run Kubernetes on AWS without needing to install and operate your own Kubernetes control plane or nodes. In this lesson, we'll deploy a complete EKS cluster with:

- A VPC with public and private subnets across multiple availability zones
- An EKS cluster with managed node groups
- Proper security groups and IAM roles
- Auto-scaling capabilities

## Infrastructure Components

### 1. VPC (Virtual Private Cloud)
- **CIDR**: 10.0.0.0/16
- **Availability Zones**: 3 zones (us-east-2a, us-east-2b, us-east-2c)
- **Public Subnets**: 10.0.4.0/24, 10.0.5.0/24, 10.0.6.0/24
- **Private Subnets**: 10.0.1.0/24, 10.0.2.0/24, 10.0.3.0/24
- **NAT Gateway**: Single NAT gateway for cost optimization
- **Internet Gateway**: For public subnet internet access

### 2. EKS Cluster
- **Name**: demo-eks-{random-suffix}
- **Version**: Kubernetes 1.32
- **Endpoint**: Public access enabled
- **Logging**: API, audit, and authenticator logs enabled
- **Encryption**: Secrets encryption enabled

### 3. Managed Node Groups
- **Node Group 1**: 
  - Instance type: t3.micro
  - Min: 1, Max: 3, Desired: 2
- **Node Group 2**:
  - Instance type: t3.micro
  - Min: 1, Max: 2, Desired: 1

## Terraform Configuration

### File Structure
```
terraform-provison-eks/
├── main.tf              # Main configuration and providers
├── variables.tf         # Input variables
├── outputs.tf          # Output values
├── provider.tf         # Provider requirements
├── vpc.tf              # VPC configuration
└── eks-cluster.tf      # EKS cluster configuration
```

### Key Configuration Files

#### 1. provider.tf
```hcl
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.46.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.4.3"
    }
    tls = {
      source  = "hashicorp/tls"
      version = "~> 4.0.4"
    }
    cloudinit = {
      source  = "hashicorp/cloudinit"
      version = "~> 2.2.0"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.16.1"
    }
  }
  required_version = "~> 1.3"
}
```

#### 2. variables.tf
```hcl
variable "region" {
  description = "AWS region"
  type        = string
  default     = "us-east-2"
}
```

#### 3. main.tf
```hcl
provider "kubernetes" {
  host                   = module.eks.cluster_endpoint
  cluster_ca_certificate = base64decode(module.eks.cluster_certificate_authority_data)
}

provider "aws" {
  region = var.region
}

data "aws_availability_zones" "available" {}

locals {
  cluster_name = "demo-eks-${random_string.suffix.result}"
}

resource "random_string" "suffix" {
  length  = 8
  special = false
}
```

#### 4. vpc.tf
```hcl
module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "3.14.2"

  name = "Demo-VPC"
  cidr = "10.0.0.0/16"
  azs  = slice(data.aws_availability_zones.available.names, 0, 3)

  private_subnets = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
  public_subnets  = ["10.0.4.0/24", "10.0.5.0/24", "10.0.6.0/24"]

  enable_nat_gateway     = true
  single_nat_gateway     = true
  enable_dns_hostnames   = true

  public_subnet_tags = {
    "kubernetes.io/cluster/${local.cluster_name}" = "shared"
    "kubernetes.io/role/elb"                      = 1
  }

  private_subnet_tags = {
    "kubernetes.io/cluster/${local.cluster_name}" = "shared"
    "kubernetes.io/role/internal-elb"             = 1
  }
}
```

#### 5. eks-cluster.tf
```hcl
module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "19.0.4"

  cluster_name    = local.cluster_name
  cluster_version = "1.32"

  vpc_id                         = module.vpc.vpc_id
  subnet_ids                     = module.vpc.private_subnets
  cluster_endpoint_public_access = true

  eks_managed_node_group_defaults = {
    ami_type = "AL2_x86_64"
  }

  eks_managed_node_groups = {
    one = {
      name           = "node-group-1"
      instance_types = ["t3.micro"]
      min_size       = 1
      max_size       = 3
      desired_size   = 2
    }

    two = {
      name           = "node-group-2"
      instance_types = ["t3.micro"]
      min_size       = 1
      max_size       = 2
      desired_size   = 1
    }
  }
}
```

#### 6. outputs.tf
```hcl
output "cluster_name" {
  description = "Amazon Web Service EKS Cluster Name"
  value       = module.eks.cluster_name
}

output "cluster_endpoint" {
  description = "Endpoint for Amazon Web Service EKS"
  value       = module.eks.cluster_endpoint
}

output "region" {
  description = "Amazon Web Service EKS Cluster region"
  value       = var.region
}

output "cluster_security_group_id" {
  description = "Security group ID for the Amazon Web Service EKS Cluster"
  value       = module.eks.cluster_security_group_id
}
```

## Step-by-Step Implementation

### Step 1: Environment Setup

1. **Navigate to the project directory:**
   ```bash
   cd terraform-provison-eks
   ```

2. **Verify AWS CLI configuration:**
   ```bash
   aws sts get-caller-identity
   ```

3. **Check Terraform version:**
   ```bash
   terraform version
   ```

### Step 2: Initialize Terraform

```bash
terraform init
```

**Expected Output:**
- Terraform will download required providers
- Modules will be downloaded (EKS and VPC modules)
- Lock file (.terraform.lock.hcl) will be created

### Step 3: Plan the Deployment

```bash
terraform plan
```

**What to expect:**
- Terraform will show 54 resources to be created
- Review the plan carefully
- Key resources include:
  - VPC and networking components
  - EKS cluster and security groups
  - IAM roles and policies
  - Managed node groups
  - KMS key for encryption

### Step 4: Apply the Configuration

```bash
terraform apply
```

**When prompted, type `yes` to confirm the deployment.**

**Expected Output:**
```
Apply complete! Resources: 54 added, 0 changed, 0 destroyed.

Outputs:

cluster_endpoint = "https://96215CD466AA0F9C343287EF8F69D50D.gr7.us-east-2.eks.amazonaws.com"
cluster_name = "demo-eks-oL0oTGZv"
cluster_security_group_id = "sg-03a102ce0d6e701ae"
region = "us-east-2"
```

### Step 5: Configure kubectl

```bash
aws eks update-kubeconfig --region us-east-2 --name demo-eks-oL0oTGZv
```

**Note:** Replace `demo-eks-oL0oTGZv` with your actual cluster name from the output.

## Verification and Testing

### Step 1: Verify Cluster Connection

```bash
kubectl get nodes
```

**Expected Output:**
```
NAME                                       STATUS   ROLES    AGE   VERSION
ip-10-0-1-15.us-east-2.compute.internal    Ready    <none>   39m   v1.32.8-eks-99d6cc0
ip-10-0-1-220.us-east-2.compute.internal   Ready    <none>   38m   v1.32.8-eks-99d6cc0
ip-10-0-2-197.us-east-2.compute.internal   Ready    <none>   39m   v1.32.8-eks-99d6cc0
```

### Step 2: Check Namespaces

```bash
kubectl get namespaces
```

**Expected Output:**
```
NAME              STATUS   AGE
default           Active   46m
kube-node-lease   Active   46m
kube-public       Active   46m
kube-system       Active   46m
```

### Step 3: Verify AWS Console

1. **Go to AWS Console** → **Region: us-east-2**

2. **Check VPC:**
   - Navigate to VPC → Your VPCs
   - Verify "Demo-VPC" exists

3. **Check NAT Gateway:**
   - Navigate to VPC → NAT Gateways
   - Verify "Demo-VPC-us-east-2a" exists

4. **Check EKS Cluster:**
   - Navigate to EKS → Clusters
   - Verify your cluster (e.g., "demo-eks-oL0oTGZv") exists

5. **Check EC2 Instances:**
   - Navigate to EC2 → Instances
   - Verify 3 instances are running (2 from node-group-1, 1 from node-group-2)

### Step 4: Test Application Deployment

Deploy a simple nginx application to test the cluster:

```bash
kubectl create deployment nginx --image=nginx
kubectl expose deployment nginx --port=80 --type=LoadBalancer
```

Check the deployment:
```bash
kubectl get pods
kubectl get services
```

## Cleanup

### Step 1: Delete Test Resources

```bash
kubectl delete service nginx
kubectl delete deployment nginx
```

### Step 2: Destroy Infrastructure

```bash
terraform destroy
```

**When prompted, type `yes` to confirm the destruction.**

**Expected Output:**
```
Destroy complete! Resources: 54 destroyed.
```

### Step 3: Verify Cleanup

1. Check AWS Console to ensure all resources are deleted
2. Verify no running EC2 instances
3. Verify EKS cluster is deleted
4. Verify VPC and related networking components are removed

## Troubleshooting

### Common Issues and Solutions

#### 1. Terraform Init Fails
**Problem:** Provider download issues
**Solution:** 
```bash
rm -rf .terraform
terraform init
```

#### 2. AWS Permissions Error
**Problem:** Insufficient permissions
**Solution:** Ensure your AWS user/role has:
- EKSFullAccess
- IAMFullAccess
- VPCFullAccess
- EC2FullAccess

#### 3. kubectl Connection Issues
**Problem:** Cannot connect to cluster
**Solution:**
```bash
aws eks update-kubeconfig --region us-east-2 --name YOUR_CLUSTER_NAME
```

#### 4. Node Group Not Ready
**Problem:** Nodes stuck in NotReady state
**Solution:**
- Check security group rules
- Verify IAM roles are properly attached
- Check CloudWatch logs for node group issues

#### 5. VPC Subnet Issues
**Problem:** Subnet configuration errors
**Solution:**
- Ensure subnets are in different availability zones
- Verify CIDR blocks don't overlap
- Check subnet tags for EKS

### Useful Commands for Debugging

```bash
# Check cluster status
kubectl cluster-info

# Describe nodes for detailed information
kubectl describe nodes

# Check events
kubectl get events --sort-by=.metadata.creationTimestamp

# Check AWS EKS cluster status
aws eks describe-cluster --name YOUR_CLUSTER_NAME --region us-east-2
```

## Key Concepts Summary

### 1. EKS Architecture
- **Control Plane**: Managed by AWS, runs in AWS account
- **Data Plane**: Worker nodes in your account
- **Networking**: VPC with public/private subnets
- **Security**: IAM roles, security groups, encryption

### 2. Managed Node Groups
- AWS manages the lifecycle of worker nodes
- Auto-scaling capabilities
- Automatic updates and patching
- Integration with AWS services

### 3. Networking
- **Public Subnets**: For load balancers and NAT gateways
- **Private Subnets**: For worker nodes
- **Security Groups**: Control traffic flow
- **Subnet Tags**: Required for EKS integration

### 4. Security
- **IAM Roles**: For cluster and node permissions
- **KMS Encryption**: For secrets and data encryption
- **Security Groups**: Network-level security
- **RBAC**: Kubernetes role-based access control

### 5. Cost Optimization
- Single NAT Gateway (vs. one per AZ)
- t3.micro instances for learning
- Auto-scaling to match demand
- Proper resource tagging

### 6. Best Practices
- Use managed node groups for production
- Enable cluster logging
- Use private subnets for worker nodes
- Implement proper IAM policies
- Regular security updates
- Monitor cluster health

## Additional Resources

- [AWS EKS Documentation](https://docs.aws.amazon.com/eks/)
- [Terraform AWS EKS Module](https://registry.terraform.io/modules/terraform-aws-modules/eks/aws/latest)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [AWS EKS Best Practices](https://aws.github.io/aws-eks-best-practices/)

## Exercise Questions

1. **Architecture Understanding:**
   - Why do we use private subnets for worker nodes?
   - What is the purpose of the NAT gateway in this setup?

2. **Scaling:**
   - How would you modify the configuration to add a third node group?
   - What happens when you change the `desired_size` of a node group?

3. **Security:**
   - What IAM policies are required for the EKS cluster?
   - How does encryption work in this EKS setup?

4. **Networking:**
   - Explain the subnet tagging strategy used in this configuration
   - What would happen if you removed the internet gateway?

5. **Cost Optimization:**
   - How could you reduce costs while maintaining high availability?
   - What are the trade-offs of using a single NAT gateway?

---

**Note:** This guide provides a comprehensive walkthrough of deploying AWS EKS with Terraform. Always follow AWS best practices and consider your specific requirements when implementing in production environments.
