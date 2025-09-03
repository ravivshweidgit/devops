# Terraform AWS: Taint and Debugging - Student Guide

**Course:** [Terraform for Beginners - KodeKloud](https://learn.kodekloud.com/user/courses/udemy-labs-terraform-for-beginners)

## Overview
This lesson covers essential Terraform concepts including logging, debugging, and resource tainting. You'll learn how to enable logging, export logs to specific paths, and manage resource states using taint and untaint commands.

## Learning Objectives
- Understand Terraform logging and debugging capabilities
- Learn how to set environment variables for logging
- Explore different log levels and their purposes
- Understand resource tainting and its effects
- Practice using taint and untaint commands

## Prerequisites
- Basic understanding of Terraform
- Access to AWS environment
- Familiarity with command line operations

---

## Lesson Content

### 1. Terraform Logging Environment Variables

**Question:** Which environment variable should be used to export the logs to a specific path?

**Answer:** `TF_LOG_PATH`

**Explanation:** The `TF_LOG_PATH` environment variable specifies where Terraform should write its log output. This is essential for debugging and troubleshooting Terraform operations.

---

### 2. Logging Configuration Requirements

**Question:** Can you export the debug logs from terraform just by setting TF_LOG_PATH environment variable and providing a path as the value to this variable?

**Answer:** **NO**

**Explanation:** Setting only `TF_LOG_PATH` is not sufficient. You also need to set the `TF_LOG` environment variable to specify the log level (e.g., ERROR, DEBUG, TRACE).

---

### 3. Practical Exercise: Setting Up Logging

**Task:** We have a configuration directory called `/root/terraform-projects/ProjectA`. Enable logging with the log level set to ERROR and then export the logs to the path `/tmp/ProjectA.log`. Once the environment variables are set, run a terraform init and apply.

**Solution:**
```bash
cd /root/terraform-projects/ProjectA
export TF_LOG=ERROR
export TF_LOG_PATH=/tmp/ProjectA.log
terraform init
terraform apply
```

**Expected Output:**
```
Enter a value: yes

aws_instance.ProjectA: Creating...
╷
│ Error: creating EC2 Instance: AuthFailure: AWS was not able to validate the provided access credentials
│       status code: 401, request id: ae7655b3-1c10-4d3d-9927-048e3d323cf8
│ 
│   with aws_instance.ProjectA,
│   on main.tf line 1, in resource "aws_instance" "ProjectA":
│    1: resource "aws_instance" "ProjectA" {
```

**Note:** It's OK if this results in an error. Do not change any configuration files before you export the logs!

---

### 4. Log Levels in Terraform

**Question:** Which Log Level provides the most details when you run terraform commands?

**Answer:** **TRACE**

**Explanation:** The TRACE log level provides the most comprehensive and detailed information about Terraform operations, including low-level details about API calls, resource state changes, and internal processes.

---

### 5. Resource Provisioning Exercise

**Task:** Navigate to `/root/terraform-projects/ProjectB`. We already have a main.tf file created for provisioning an AWS EC2 instance with the tag Name: projectb_webserver. Run a terraform init and apply to provision this instance.

**Solution:**
```bash
cd ../ProjectB
terraform init
terraform apply
```

**Expected Output:**
```
Enter a value: yes

aws_instance.ProjectB: Creating...
aws_instance.ProjectB: Still creating... [10s elapsed]
aws_instance.ProjectB: Creation complete after 10s [id=i-7204508d51cc45d9a]

Apply complete! Resources: 1 added, 0 changed, 0 destroyed.
```

---

### 6. Understanding Tainted Resources

**Task:** Now, try running a terraform plan again. What is the effect?

**Expected Output:**
```
# aws_instance.ProjectB is tainted, so must be replaced
Resources will be replaced
```

**Explanation:** When a resource is tainted, Terraform marks it for replacement. The next `terraform plan` or `terraform apply` will destroy and recreate the tainted resource.

---

### 7. Resource Tainting Explanation

**Question:** Why is the resource called ProjectB being replaced?

**Answer:** **ProjectB resource is Tainted**

**Explanation:** Tainted resources are marked for replacement because Terraform considers them in an inconsistent or problematic state. This could happen due to manual tainting, failed operations, or other issues that make Terraform want to recreate the resource.

---

### 8. Untainting Resources

**Task:** Untaint the resource called ProjectB so that the resource is not replaced any more.

**Solution:**
```bash
terraform untaint aws_instance.ProjectB
```

**Expected Output:**
```
Resource instance aws_instance.ProjectB has been successfully untainted.
```

**Explanation:** The `terraform untaint` command removes the tainted state from a resource, preventing it from being replaced in subsequent operations.

---

## Key Concepts Summary

### Environment Variables for Logging
- **`TF_LOG`**: Sets the log level (ERROR, WARN, INFO, DEBUG, TRACE)
- **`TF_LOG_PATH`**: Specifies the file path for log output

### Log Levels (from least to most detailed)
1. **ERROR**: Only error messages
2. **WARN**: Warning and error messages
3. **INFO**: General information, warnings, and errors
4. **DEBUG**: Detailed debugging information
5. **TRACE**: Most comprehensive logging level

### Resource Tainting
- **Taint**: Marks a resource for replacement
- **Untaint**: Removes the tainted state
- **Effect**: Tainted resources are destroyed and recreated on next apply

---

## Practice Exercises

1. **Logging Setup**: Practice setting different log levels and exporting logs to various paths
2. **Resource Management**: Experiment with tainting and untainting resources
3. **Debugging**: Use logs to troubleshoot common Terraform issues

---

## Additional Resources

- [Terraform Documentation - Logging](https://www.terraform.io/docs/internals/debugging.html)
- [Terraform CLI Commands](https://www.terraform.io/docs/cli/commands/index.html)
- [AWS Provider Documentation](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)

---

## Next Steps

After completing this lesson, you should be able to:
- Configure Terraform logging for debugging
- Understand and manage resource tainting
- Use logs to troubleshoot Terraform operations
- Apply best practices for resource state management

---

*This guide is based on the KodeKloud Terraform for Beginners course. For the most up-to-date information, always refer to the official Terraform documentation.*
