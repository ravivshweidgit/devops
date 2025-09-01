# Terraform AWS S3 Buckets - Student Guide

## Overview
This lab focuses on working with Amazon S3 buckets using Terraform. You'll learn how to create, configure, and manage S3 buckets and objects through Infrastructure as Code (IaC) principles.

## Prerequisites
- Basic understanding of Terraform
- Familiarity with AWS S3 concepts
- Access to a Terraform environment with AWS provider configured

## Lab Structure
The lab is organized into three main configuration directories:
- **MCU**: Pre-configured S3 bucket setup
- **DC**: Creating a new S3 bucket from scratch
- **Pixar**: Uploading objects to an existing S3 bucket

---

## Section 1: MCU Configuration Directory

### Step 1: Understanding Provider Configuration

Navigate to the MCU directory and examine the configuration files:

#### `provider.tf`
```hcl
terraform {
  required_providers {
    aws = {
      source = "hashicorp/aws"
      version = "4.15.0"
    }
  }
}

provider "aws" {
  region                      = var.region
  s3_use_path_style = true
  skip_credentials_validation = true
  skip_requesting_account_id  = true

  endpoints {
    s3                       = "http://aws:4566"
  }
}
```

**Key Points:**
- Uses AWS provider version 4.15.0
- Region is set via variable reference (`var.region`)
- Configured for local development with LocalStack (`http://aws:4566`)
- Path-style addressing enabled for S3

#### `variables.tf`
```hcl
variable "region" {
}
```

#### `terraform.tfvars`
```hcl
region = "us-east-1"
```

**Question 1:** What is the AWS region configured for use in the provider block?
**Answer:** `us-east-1`

### Step 2: Understanding Resource Configuration

#### `main.tf`
```hcl
resource "aws_s3_bucket" "marvel-cinematic-universe" {
  bucket = "mcu-202011121359"
}
```

**Key Concepts:**
- `aws_s3_bucket` is the resource type
- `marvel-cinematic-universe` is the resource name (local identifier)
- `bucket` argument specifies the actual S3 bucket name

**Question 2:** What is the resource name that will be provisioned?
**Answer:** `marvel-cinematic-universe`

### Step 3: Checking Terraform State

**Question 3:** What is the current state of this configuration directory?
**Answer:** Since `terraform.tfstate` exists, resources have been provisioned (after apply)

### Step 4: S3 Bucket Properties

**Question 4:** What is the name of the S3 bucket that has been created?
**Answer:** `mcu-202011121359`

**Question 5:** What is the DNS domain name that is created for this bucket?

Use the following command to inspect the bucket and filter for domain information:
```bash
terraform state show aws_s3_bucket.marvel-cinematic-universe | grep domain
```

**Command Output:**
```bash
❯ terraform state show aws_s3_bucket.marvel-cinematic-universe | grep domain
    bucket_domain_name          = "mcu-202011121359.s3.amazonaws.com"
    bucket_regional_domain_name = "mcu-202011121359.s3.amazonaws.com"
```

**Answer:** `mcu-202011121359.s3.amazonaws.com`

**Alternative Method using JSON output:**
```bash
terraform show -json | jq '.values.root_module.resources[] | select(.address=="aws_s3_bucket.marvel-cinematic-universe") | .values.bucket_domain_name'
```

---

## Section 2: DC Configuration Directory

### Step 1: Creating a New S3 Bucket

Navigate to the DC directory. The `main.tf` file is empty. Create a new S3 bucket with these specifications:
- Resource name: `dc_bucket`
- Bucket name: `dc_is_better_than_marvel`

#### Initial Configuration
```hcl
resource "aws_s3_bucket" "dc_bucket" {
  bucket = "dc_is_better_than_marvel"
}
```

### Step 2: Understanding S3 Bucket Naming Rules

**Question 6:** Why did the terraform apply command fail?

**Error Message:**
```
Error: error creating S3 Bucket (dc_is_better_than_marvel): InvalidBucketName: The specified bucket is not valid.
```

**Answer:** Invalid Bucket Name

**Explanation:** S3 bucket names must follow DNS naming conventions:
- Cannot contain underscores (`_`)
- Must use only lowercase letters, numbers, hyphens (`-`), and periods (`.`)
- Must be between 3 and 63 characters long
- Must start and end with a letter or number

### Step 3: Fixing the Bucket Name

Update the configuration to use hyphens instead of underscores:

```hcl
resource "aws_s3_bucket" "dc_bucket" {
  bucket = "dc-is-better-than-marvel"
}
```

**Success Output:**
```
aws_s3_bucket.dc_bucket: Creating...
aws_s3_bucket.dc_bucket: Creation complete after 0s [id=dc-is-better-than-marvel]

Apply complete! Resources: 1 added, 0 changed, 0 destroyed.
```

---

## Section 3: Pixar Configuration Directory

### Step 1: Working with Existing Buckets

Navigate to the Pixar directory. This section demonstrates how to work with existing S3 buckets (created via AWS CLI) and upload objects to them.

### Step 2: Uploading Objects to S3

Create a configuration to upload the `woody.jpg` file to the existing `pixar-studios-2020` bucket:

#### Configuration
```hcl
resource "aws_s3_object" "upload" {
  bucket = "pixar-studios-2020"
  key    = "woody.jpg"
  source = "/root/woody.jpg"
}
```

**Key Concepts:**
- `aws_s3_object` resource type for uploading files
- `bucket`: Target S3 bucket name
- `key`: Object key (filename in S3)
- `source`: Local file path to upload

**Success Output:**
```
aws_s3_object.upload: Creating...
aws_s3_object.upload: Creation complete after 0s [id=woody.jpg]

Apply complete! Resources: 1 added, 0 changed, 0 destroyed.
```

---

## Key Learning Objectives

### 1. Terraform Provider Configuration
- Understanding provider blocks and version constraints
- Configuring AWS provider for different environments
- Using variables for dynamic configuration

### 2. S3 Bucket Creation
- Resource syntax and structure
- Bucket naming conventions and restrictions
- State management and resource tracking

### 3. S3 Object Management
- Uploading files to existing buckets
- Understanding object keys and paths
- Managing file uploads through IaC

### 4. Terraform Commands
- `terraform init`: Initialize working directory
- `terraform plan`: Preview changes
- `terraform apply`: Apply configuration
- `terraform state show`: Inspect resource state
- `terraform show -json`: Get JSON output for scripting

### 5. Best Practices
- Use meaningful resource names
- Follow S3 naming conventions
- Leverage variables for configuration
- Understand state management
- Use proper error handling

---

## Common Issues and Solutions

### 1. Invalid Bucket Names
**Problem:** Bucket names with underscores or invalid characters
**Solution:** Use only lowercase letters, numbers, and hyphens

### 2. Provider Configuration
**Problem:** Missing or incorrect provider configuration
**Solution:** Ensure provider block is properly configured with required arguments

### 3. State Management
**Problem:** Resources not found in state
**Solution:** Run `terraform init` and `terraform plan` to sync state

---

## Additional Resources

- [Terraform AWS Provider Documentation](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [AWS S3 Bucket Naming Rules](https://docs.aws.amazon.com/AmazonS3/latest/userguide/bucketnamingrules.html)
- [Terraform State Management](https://www.terraform.io/docs/language/state/index.html)

---

## Lab Completion Checklist

- [ ] Successfully identified AWS region in MCU configuration
- [ ] Understood resource naming conventions
- [ ] Created S3 bucket in DC directory with proper naming
- [ ] Uploaded object to existing bucket in Pixar directory
- [ ] Executed all terraform commands successfully
- [ ] Understood error handling and troubleshooting

**Congratulations!** You have successfully completed the Terraform AWS S3 lab and learned the fundamentals of managing S3 resources through Infrastructure as Code.
