# Terraform AWS - Importing Existing Resources
## Student Guide

**Course:** [Terraform for Beginners - KodeKloud Labs](https://learn.kodekloud.com/user/courses/udemy-labs-terraform-for-beginners)

**Lesson:** Terraform Import - Managing Existing AWS Resources

---

## Overview

This lesson demonstrates how to use Terraform's `import` functionality to bring existing AWS resources under Terraform management. You'll learn how to:

1. Inspect existing Terraform configurations
2. Identify resources not managed by Terraform
3. Import existing AWS resources into Terraform state
4. Configure resource blocks to match imported resources
5. Ensure Terraform can manage imported resources without conflicts

---

## Prerequisites

- Basic understanding of Terraform syntax
- Familiarity with AWS EC2 concepts
- Access to a KodeKloud lab environment
- Terraform CLI installed and configured

---

## Lab Environment Setup

**Working Directory:** `/root/terraform-projects/project-jade`

**AWS Configuration:** This lab uses a local AWS test framework (LocalStack) accessible at `http://aws:4566`

---

## Step-by-Step Guide

### Step 1: Navigate and Inspect the Project

```bash
cd terraform-projects/project-jade/
```

**Files to examine:**
- `main.tf` - Main Terraform configuration
- `provider.tf` - AWS provider configuration
- `variables.tf` - Variable definitions

### Step 2: Understand the Existing Configuration

#### main.tf
```hcl
resource "aws_instance" "ruby" {
  ami           = var.ami
  instance_type = var.instance_type
  for_each      = var.name
  key_name      = var.key_name
  tags = {
    Name = each.value
  }
}

output "instances" {
  value = aws_instance.ruby
}
```

**Key Points:**
- Uses `for_each` to create multiple instances
- Each instance gets a unique name from the `name` variable
- All instances share the same AMI, instance type, and key pair

#### provider.tf
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
  region                      = "us-east-1"
  skip_credentials_validation = true
  skip_requesting_account_id  = true

  endpoints {
    ec2 = "http://aws:4566"
  }
}
```

**Key Points:**
- Uses AWS provider version 4.15.0
- Configured for local testing environment
- Endpoint points to local AWS mock service

#### variables.tf
```hcl
variable "name" {
  type    = set(string)
  default = ["jade-webserver", "jade-lbr", "jade-app1", "jade-agent", "jade-app2"]
}

variable "ami" {
  default = "ami-0c9bfc21ac5bf10eb"
}

variable "instance_type" {
  default = "t2.nano"
}

variable "key_name" {
  default = "jade"
}
```

**Key Points:**
- Creates 5 EC2 instances with different names
- All instances use `t2.nano` instance type
- All instances use the `jade` SSH key pair

### Step 3: Examine Current Terraform State

```bash
terraform state list
```

**Expected Output:**
```
aws_instance.ruby["jade-agent"]
aws_instance.ruby["jade-app1"]
aws_instance.ruby["jade-app2"]
aws_instance.ruby["jade-lbr"]
aws_instance.ruby["jade-webserver"]
```

**Analysis:**
- 5 EC2 instances managed by Terraform
- All follow the naming pattern defined in variables
- No standalone resources outside the `for_each` loop

### Step 4: Identify the SSH Key

**Question:** What is the name of the SSH key used by all instances?

**Answer:** `jade`

**Evidence:** Defined in `variables.tf`:
```hcl
variable "key_name" {
  default = "jade"
}
```

**Important Note:** The key pair resource is NOT created by this Terraform configuration. It was created separately using AWS CLI:

```bash
aws ec2 create-key-pair --endpoint http://aws:4566 --key-name jade --query 'KeyMaterial' --output text > /root/terraform-projects/project-jade/jade.pem
```

### Step 5: Discover Unmanaged Resources

**Scenario:** There's another EC2 instance called `jade-mw` created outside Terraform.

**Specifications:**
- AMI: `ami-082b3eca746b12a89`
- Instance Type: `t2.large`
- Key Name: `jade`

**Find the Instance ID:**
```bash
aws ec2 describe-instances --endpoint http://aws:4566 --filters "Name=tag:Name,Values=jade-mw" --query 'Reservations[].Instances[].InstanceId'
```

**Expected Output:**
```json
[
    "i-f91fd1d818370c040"
]
```

### Step 6: Create Resource Block for Import

Add an empty resource block to `main.tf`:

```hcl
resource "aws_instance" "jade-mw" {
}
```

**Note:** We'll fill in the arguments after importing.

### Step 7: Import the Resource

```bash
terraform import aws_instance.jade-mw "i-f91fd1d818370c040"
```

**Expected Output:**
```
aws_instance.jade-mw: Importing from ID "i-f91fd1d818370c040"...
aws_instance.jade-mw: Import prepared!
  Prepared aws_instance for import
aws_instance.jade-mw: Refreshing state... [id=i-f91fd1d818370c040]

Import successful!

The resources that were imported are shown above. These resources are now in
your Terraform state and will henceforth be managed by Terraform
```

**What Happens:**
- Terraform reads the current state of the EC2 instance
- Adds it to the Terraform state file
- The resource is now tracked by Terraform

### Step 8: Inspect Imported Resource State

```bash
terraform state show aws_instance.jade-mw
```

**Key Attributes to Extract:**
```bash
# Extract AMI
terraform state show aws_instance.jade-mw | grep ami
# Output: ami = "ami-082b3eca746b12a89"

# Extract instance type
terraform state show aws_instance.jade-mw | grep instance_type
# Output: instance_type = "t2.large"

# Extract key name
terraform state show aws_instance.jade-mw | grep key_name
# Output: key_name = "jade"
```

### Step 9: Complete the Resource Block

Update the resource block with the extracted values:

```hcl
resource "aws_instance" "jade-mw" {
  ami           = "ami-082b3eca746b12a89"
  instance_type = "t2.large"
  key_name      = "jade"
  tags = {
    Name = "jade-mw"
  }
}
```

**Why This is Necessary:**
- Without these arguments, Terraform would try to destroy the instance
- The configuration must match the actual resource state
- This prevents conflicts between desired and actual state

### Step 10: Verify Configuration

```bash
terraform plan
```

**Expected Result:** No changes to apply (or minimal changes like adding `user_data_replace_on_change`)

**If Changes Are Detected:**
- Review the plan output carefully
- Ensure all required attributes are defined
- Avoid adding `user_data_replace_on_change` attribute as instructed

### Step 11: Apply the Configuration

```bash
terraform apply
```

**Expected Output:**
- Minimal changes (usually just metadata updates)
- No resource destruction
- All resources remain running

---

## Key Concepts Explained

### 1. Terraform Import

**Purpose:** Bring existing infrastructure under Terraform management

**Process:**
1. Create empty resource block
2. Import existing resource using `terraform import`
3. Extract resource attributes from state
4. Complete resource block configuration
5. Verify no conflicts with `terraform plan`

### 2. State Management

**Before Import:**
- Resource exists in AWS but not in Terraform state
- Terraform unaware of the resource
- Cannot manage or track changes

**After Import:**
- Resource tracked in Terraform state
- Terraform can manage the resource
- Changes can be applied through Terraform

### 3. Configuration Matching

**Critical Requirement:** The resource block must match the actual resource state

**Common Attributes:**
- `ami` - Amazon Machine Image ID
- `instance_type` - EC2 instance type
- `key_name` - SSH key pair name
- `tags` - Resource tags
- `subnet_id` - VPC subnet (if applicable)

### 4. Import Best Practices

1. **Always inspect state first** - Use `terraform state show` to understand current configuration
2. **Match configuration exactly** - Ensure all attributes are defined
3. **Test with plan** - Always run `terraform plan` before applying
4. **Document changes** - Keep track of what was imported and why

---

## Common Pitfalls and Solutions

### Pitfall 1: Missing Required Attributes

**Problem:** Terraform tries to destroy imported resource
**Solution:** Ensure all required attributes are defined in the resource block

### Pitfall 2: Configuration Mismatch

**Problem:** `terraform plan` shows unexpected changes
**Solution:** Compare resource block with actual state using `terraform state show`

### Pitfall 3: Importing Wrong Resource

**Problem:** Importing resource with different specifications
**Solution:** Double-check resource ID and verify with AWS CLI before importing

---

## Verification Checklist

- [ ] Resource successfully imported into Terraform state
- [ ] Resource block configuration matches actual resource state
- [ ] `terraform plan` shows no destructive changes
- [ ] `terraform apply` completes successfully
- [ ] All resources remain running and accessible
- [ ] No configuration conflicts detected

---

## Summary

This lesson demonstrates the power of Terraform's import functionality to bring existing infrastructure under management. Key takeaways:

1. **Import Process:** Create resource block → Import resource → Configure attributes → Verify configuration
2. **State Management:** Imported resources become part of Terraform's state and can be managed
3. **Configuration Matching:** Resource blocks must accurately reflect actual resource state
4. **Verification:** Always use `terraform plan` to verify no conflicts before applying

The ability to import existing resources is crucial for organizations adopting Terraform, as it allows gradual migration of infrastructure without rebuilding from scratch.

---

## Additional Resources

- [Terraform Import Documentation](https://developer.hashicorp.com/terraform/cli/import)
- [AWS Provider Documentation](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [Terraform State Management](https://developer.hashicorp.com/terraform/language/state)

---

## Lab Completion

**Congratulations!** You have successfully:
- Imported an existing EC2 instance into Terraform
- Configured the resource block to match the actual state
- Verified that Terraform can manage the imported resource
- Applied the configuration without conflicts

This skill is essential for real-world Terraform implementations where you need to manage existing infrastructure alongside new deployments.
