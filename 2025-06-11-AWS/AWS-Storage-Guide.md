# AWS Storage Resources - Complete Guide

## Overview

This document covers three primary AWS storage services:
- **EBS (Elastic Block Store)** - Block-level storage for EC2 instances
- **S3 (Simple Storage Service)** - Object storage service
- **EFS (Elastic File System)** - Managed NFS file system

---

## S3 (Simple Storage Service) Class

### Introduction to S3
Amazon S3 is an object storage service that offers industry-leading scalability, data availability, security, and performance. S3 buckets have globally unique names and can store unlimited amounts of data.

### Hands-On Exercise: Creating and Managing S3 Bucket

#### Step 1: Create S3 Bucket
1. Navigate to AWS Console search bar
2. Search for "s3" and select S3 service
3. Click "Create bucket"
4. **Bucket name**: `raviv-shweid-s3-demo` (must be globally unique)
5. Click "Create bucket"

#### Step 2: Upload Content
1. Download a sample image from [Unsplash](https://unsplash.com/photos/gray-wooden-house-178j8tJrNlc)
2. Upload the JPG file to your S3 bucket
3. Navigate back to bucket overview

#### Step 3: Understanding S3 Access Control
**Default Behavior**: No public access
- When you copy the file URL and paste it in browser: **AccessDenied**
- S3 objects are private by default

#### Step 4: Creating Presigned URLs
1. In bucket → select your file → Actions
2. Choose "Share with presigned URL"
3. Set duration: 1 minute
4. Click "Create presigned URL"
5. The URL is automatically copied to clipboard
6. Paste in browser - you can now access the image

**Important**: After the specified time (1 minute), the URL expires and returns:
```xml
<Code>AccessDenied</Code>
<Message>Request has expired</Message>
```

### AWS CLI Integration

#### Using CloudShell
AWS CloudShell provides a browser-based shell with pre-installed AWS CLI and inherits your user privileges.

#### Basic AWS CLI Commands
```bash
# Basic AWS CLI help
aws help

# Copy file from S3 to local directory
aws s3 cp s3://raviv-shweid-s3-demo/todd-kent-178j8tJrNlc-unsplash.jpg .

# List files
ll
```

**Sample Output**:
```bash
download: s3://raviv-shweid-s3-demo/todd-kent-178j8tJrNlc-unsplash.jpg to ./todd-kent-178j8tJrNlc-unsplash.jpg
total 7076
-rw-r--r--. 1 cloudshell-user cloudshell-user 7243272 Jun 11 17:25 todd-kent-178j8tJrNlc-unsplash.jpg
```

**Key Point**: AWS CLI is a wrapper around S3 API calls.

### S3 Lifecycle Management

#### Creating Lifecycle Rules
1. Navigate to bucket → Management tab
2. Click "Create lifecycle rule"
3. **Lifecycle rule actions**: Check "Transition current versions of objects between storage classes"
4. **Choose storage class**: Glacier Deep Archive
5. **Days after object creation**: 180

**Purpose**: Automatically move objects to cheaper storage classes based on age and access patterns.

**Storage Classes Overview**:
- **Standard**: Frequently accessed data
- **Standard-IA**: Infrequently accessed data
- **Glacier**: Long-term archival (minutes to hours retrieval)
- **Glacier Deep Archive**: Lowest cost archival (12+ hours retrieval)

### Cleanup Process

#### Deleting S3 Resources
1. **Empty bucket first**: Select bucket → Empty bucket → Permanently delete
2. **Copy ARN for reference**: `arn:aws:s3:::raviv-shweid-s3-demo`
3. **Delete bucket**: Select bucket → Delete → Confirm deletion

**Note**: ARN (Amazon Resource Name) is the unique identifier for AWS resources.

---

## EFS (Elastic File System) Class

### Introduction to EFS
Amazon EFS provides a simple, scalable, fully managed elastic NFS file system for use with AWS services and on-premises resources.

### Hands-On Exercise: Creating and Mounting EFS

#### Step 1: Create EFS File System
1. Search for "efs" in AWS Console
2. Click "Create file system"
3. **Name**: `efs-01`
4. **VPC**: Use default VPC
5. Click "Create file system"

#### Step 2: Configure Security Groups
1. Navigate to created EFS → View details → Network tab
2. Copy the security group ID: `sg-032d8ef946aa5c4f4`
3. Go to EC2 → Security Groups → Select the copied SG
4. **Inbound rules** → Edit inbound rules → Add rule
5. **Type**: NFS
6. **Source**: 0.0.0.0/0 (for demo purposes)
7. Save rules

**Security Note**: In production, restrict source to specific VPC or security groups.

#### Step 3: Mount EFS on EC2 Instances

##### Get Mount Command
1. Select EFS → Click "Attach" (top right)
2. Copy mount command: 
```bash
sudo mount -t efs -o tls fs-088fce048ec59b7e3:/ efs
```

##### Mount on EC2-01
```bash
# Install EFS utilities
sudo yum install -y amazon-efs-utils

# Create mount point
sudo mkdir efs

# Mount EFS
sudo mount -t efs -o tls fs-088fce048ec59b7e3:/ efs

# Verify mount
df -h
```

**Expected Output**:
```bash
Filesystem        Size  Used Avail Use% Mounted on
devtmpfs          4.0M     0  4.0M   0% /dev
tmpfs             453M     0  453M   0% /dev/shm
tmpfs             181M  488K  181M   1% /run
/dev/nvme0n1p1    8.0G  1.6G  6.4G  20% /
tmpfs             453M     0  453M   0% /tmp
/dev/nvme0n1p128   10M  1.3M  8.7M  13% /boot/efi
tmpfs              91M     0   91M   0% /run/user/1000
127.0.0.1:/       8.0E     0  8.0E   0% /home/ec2-user/efs
```

##### Test Shared Storage
**On EC2-01**:
```bash
cd efs/
echo "01" > 01.txt
```

**On EC2-02**:
```bash
# Connect to second EC2 instance
ssh -i "key01.pem" ec2-user@ec2-51-21-180-135.eu-north-1.compute.amazonaws.com

# Create mount point and mount EFS
sudo mkdir efs
sudo mount -t efs -o tls fs-088fce048ec59b7e3:/ efs

# Verify shared file
cd efs/
ll
cat 01.txt
```

**Expected Output**:
```bash
total 4
-rw-r--r--. 1 root root 3 Jun 11 18:40 01.txt
01
```

### Key EFS Benefits Demonstrated
1. **Shared Storage**: Multiple EC2 instances can mount the same EFS
2. **Persistent**: Data persists beyond EC2 instance lifecycle
3. **Scalable**: Automatically scales as you add or remove files
4. **High Availability**: Built across multiple Availability Zones

### Cleanup Process
1. Terminate all EC2 instances
2. Delete EFS file system
3. Verify all resources are cleaned up

---

## Storage Services Comparison

| Feature | EBS | S3 | EFS |
|---------|-----|----|----|
| **Type** | Block Storage | Object Storage | File Storage |
| **Use Case** | Boot volumes, databases | Web content, backup, archival | Shared file systems |
| **Access** | Single EC2 instance | Internet/API | Multiple EC2 instances |
| **Scalability** | Manual scaling | Unlimited | Automatic scaling |
| **Durability** | 99.999% | 99.999999999% | 99.999999999% |
| **Pricing** | GB/month | GB/month + requests | GB/month + throughput |

---

## Best Practices

### S3 Best Practices
- Use lifecycle policies to optimize costs
- Enable versioning for critical data
- Use presigned URLs for temporary access
- Implement proper IAM policies
- Enable server-side encryption

### EFS Best Practices
- Use security groups to control access
- Consider performance modes based on workload
- Implement backup strategies
- Monitor performance metrics
- Use encryption in transit and at rest

### General Security Practices
- Never use 0.0.0.0/0 in production security groups
- Regularly audit access permissions
- Enable AWS CloudTrail for API logging
- Use least privilege principle
- Regularly rotate access keys

---

## Conclusion

This hands-on exercise demonstrated:
1. **S3**: Object storage with lifecycle management and API access
2. **EFS**: Shared file system for multiple EC2 instances
3. **AWS CLI**: Command-line interface for AWS services
4. **Security**: Proper configuration of access controls

These storage services form the foundation of AWS infrastructure and provide scalable, durable, and cost-effective solutions for various storage needs.