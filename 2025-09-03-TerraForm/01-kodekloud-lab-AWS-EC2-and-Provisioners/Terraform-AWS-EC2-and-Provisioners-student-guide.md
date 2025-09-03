# Terraform AWS EC2 and Provisioners - Student Guide

## Overview
This lab exercise covers provisioning AWS EC2 instances using Terraform, including key pair management, user data scripts, and provisioners. The lab follows the [KodeKloud Terraform for Beginners course](https://learn.kodekloud.com/user/courses/udemy-labs-terraform-for-beginners).

## Prerequisites
- Access to a Linux environment with Terraform installed
- Basic understanding of Terraform syntax
- AWS CLI configured (or using LocalStack for this lab)

## Lab Structure
The lab consists of 15 steps that progressively build a complete EC2 instance configuration with various AWS resources and Terraform features.

---

## Step 1: Initial EC2 Instance Configuration

### Objective
Create a basic EC2 instance using Terraform with variables for configuration.

### Directory Setup
```bash
cd /root/terraform-projects/project-cerberus
```

### Required Files

#### `main.tf`
```hcl
resource "aws_instance" "cerberus" {
  ami           = var.ami
  instance_type = var.instance_type
}

variable "region" {
  default = "eu-west-2"
}

variable "ami" {
  default = "ami-06178cf087598769c"
}

variable "instance_type" {
  default = "m5.large"
}
```

#### `provider.tf`
```hcl
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "4.15.0"
    }
  }
}

provider "aws" {
  region                      = var.region
  skip_credentials_validation = true
  skip_requesting_account_id  = true

  endpoints {
    ec2 = "http://aws:4566"
  }
}
```

### Commands to Execute
```bash
terraform init
terraform plan
terraform apply
```

### Expected Output
```
aws_instance.cerberus: Creating...
aws_instance.cerberus: Still creating... [10s elapsed]
aws_instance.cerberus: Creation complete after 10s [id=i-b022c9a581d7d2754]

Apply complete! Resources: 1 added, 0 changed, 0 destroyed.
```

---

## Step 2: Inspect Instance Details

### Objective
Learn how to view resource details from Terraform state.

### Command
```bash
terraform show
```

### Purpose
This command displays the resource attributes from the state file in a human-readable format, allowing you to inspect the created EC2 instance details.

---

## Step 3: Understanding SSH Key Requirements

### Objective
Recognize that the RHEL 8 AMI requires SSH key-based authentication.

### Key Points
- The AMI `ami-06178cf087598769c` is an RHEL 8 image
- It only accepts SSH key-based authentication
- No password authentication is available
- We need to create and configure a key pair

---

## Step 4: Create AWS Key Pair

### Objective
Create an AWS key pair resource using the existing SSH keys.

### SSH Keys Location
```bash
ls .ssh/*
# Output: .ssh/cerberus  .ssh/cerberus.pub
```

### Updated `main.tf`
```hcl
resource "aws_instance" "cerberus" {
  ami           = var.ami
  instance_type = var.instance_type
}

resource "aws_key_pair" "cerberus-key" {
  key_name   = "cerberus"
  public_key = file(".ssh/cerberus.pub")
}

# ... existing variables ...
```

### Commands
```bash
terraform plan
terraform apply
```

### Expected Output
```
aws_key_pair.cerberus-key: Creating...
aws_key_pair.cerberus-key: Creation complete after 0s [id=cerberus]

Apply complete! Resources: 1 added, 0 changed, 0 destroyed.
```

---

## Step 5: Associate Key Pair with EC2 Instance

### Objective
Update the EC2 instance to use the created key pair.

### Updated `main.tf`
```hcl
resource "aws_instance" "cerberus" {
  ami           = var.ami
  instance_type = var.instance_type
  key_name      = "cerberus"
}

# ... existing resources and variables ...
```

### Important Note
This change will trigger an instance replacement because the key pair is a fundamental configuration that cannot be modified on an existing instance.

### Commands
```bash
terraform plan
terraform apply
```

### Expected Output
```
Plan: 1 to add, 0 to change, 1 to destroy.

aws_instance.cerberus: Destroying... [id=i-b022c9a581d7d2754]
aws_instance.cerberus: Creating... [id=i-0220ee461968a832b]

Apply complete! Resources: 1 added, 0 changed, 1 destroyed.
```

---

## Step 6: Configure User Data Script

### Objective
Add a user data script to install nginx on the EC2 instance.

### Available Script: `install-nginx.sh`
```bash
#!/bin/bash
sudo yum update -y
sudo yum install nginx -y
sudo systemctl start nginx
```

### Updated `main.tf`
```hcl
resource "aws_instance" "cerberus" {
  ami           = var.ami
  instance_type = var.instance_type
  key_name      = "cerberus"
  user_data     = file("./install-nginx.sh")
}

# ... existing resources and variables ...
```

### Important Note
**Do not run terraform apply yet!** This is a critical learning point about user data behavior.

---

## Step 7: Understanding User Data Behavior

### Question
What will happen if we run terraform apply now?

### Answer
The current server will be modified, but nginx will not be installed.

### Explanation
User data scripts only run at first boot. When an instance is modified (even with just user data changes), it causes a reboot, not a fresh boot. Therefore, the user data script won't execute again.

---

## Step 8: Apply User Data Configuration

### Objective
Apply the updated configuration to modify the EC2 instance.

### Commands
```bash
terraform apply
```

### Expected Output
```
Plan: 0 to add, 1 to change, 0 to destroy.

aws_instance.cerberus: Modifying... [id=i-0220ee461968a832b]
aws_instance.cerberus: Modifications complete after 20s [id=i-0220ee461968a832b]

Apply complete! Resources: 0 added, 1 changed, 0 destroyed.
```

---

## Step 9: Understanding Provisioners

### Question
Where should you add a provisioner block?

### Answer
Nested block inside resource block.

### Syntax Example
```hcl
resource "aws_instance" "example" {
  # ... resource configuration ...
  
  provisioner "local-exec" {
    command = "echo 'Hello World'"
  }
}
```

---

## Step 10: Provisioner Types

### Question
Which of the following provisioners does not need a connection block defined?

### Answer
`local-exec`

### Explanation
- `local-exec`: Runs commands on the machine where Terraform is executed (local machine)
- `remote-exec`: Runs commands on the remote resource (requires connection block)
- `file`: Copies files to the remote resource (requires connection block)

---

## Step 11: Get Instance Public IP

### Objective
Retrieve the public IPv4 address of the EC2 instance.

### Command
```bash
terraform state show aws_instance.cerberus | grep public
```

### Expected Output
```
associate_public_ip_address          = true
public_dns                           = "ec2-54-214-152-11.eu-west-2.compute.amazonaws.com"
public_ip                            = "54.214.152.11"
```

### Key Information
- **Public IP**: 54.214.152.11
- **Public DNS**: ec2-54-214-152-11.eu-west-2.compute.amazonaws.com

---

## Step 12: Create Elastic IP Address

### Objective
Create a static IP address that won't change when the instance is rebooted or recreated.

### Updated `main.tf`
```hcl
resource "aws_instance" "cerberus" {
  ami           = var.ami
  instance_type = var.instance_type
  key_name      = "cerberus"
  user_data     = file("./install-nginx.sh")
}

resource "aws_eip" "eip" {
  vpc      = true
  instance = aws_instance.cerberus.id

  provisioner "local-exec" {
    command = "echo ${aws_eip.eip.public_dns} >> /root/cerberus_public_dns.txt"
  }
}

# ... existing resources and variables ...
```

### Key Features
- **vpc**: Set to `true` for VPC instances
- **instance**: References the EC2 instance ID using `aws_instance.cerberus.id`
- **provisioner**: Uses `local-exec` to write the public DNS to a file

---

## Lab Summary

### What You've Learned
1. **Basic EC2 Provisioning**: Creating EC2 instances with Terraform
2. **Variable Usage**: Implementing reusable configuration with variables
3. **Key Pair Management**: Creating and associating SSH keys with instances
4. **User Data Scripts**: Installing software during instance creation
5. **Provisioners**: Understanding different types and their use cases
6. **Elastic IPs**: Creating static IP addresses for persistent access
7. **State Management**: Using Terraform commands to inspect and manage resources

### Key Terraform Concepts Covered
- Resource blocks and their syntax
- Variable declarations and usage
- File functions (`file()`)
- Reference expressions (`aws_instance.cerberus.id`)
- Provisioner blocks and local-exec
- State inspection and management

### Best Practices Demonstrated
- Use variables for configurable values
- Separate provider configuration
- Understand resource lifecycle and replacement behavior
- Use provisioners for post-creation tasks
- Implement proper resource references

---

## Troubleshooting Tips

### Common Issues
1. **Instance Replacement**: Key pair changes trigger instance replacement
2. **User Data Limitations**: Scripts only run at first boot
3. **State File**: Always use `terraform state` commands to inspect resources
4. **Variable References**: Ensure proper syntax for resource references

### Useful Commands
```bash
terraform init          # Initialize working directory
terraform plan          # Preview changes
terraform apply         # Apply changes
terraform show          # Show current state
terraform state list    # List all resources
terraform destroy       # Clean up resources
```

---

## Next Steps
After completing this lab, consider exploring:
- Security groups and network configuration
- Data sources for dynamic resource discovery
- Output values for resource information
- Modules for reusable configurations
- Advanced provisioner types (remote-exec, file)
- Terraform workspaces and state management
