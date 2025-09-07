# Terraform Modules - Student Guide

## Overview
This guide covers the fundamentals of Terraform modules through hands-on practice with AWS IAM user creation. You'll learn how to use modules from the Terraform Registry, understand module configuration, and control resource creation through module parameters.

## Learning Objectives
By the end of this lesson, you will be able to:
- Understand what Terraform modules are and how they work
- Use modules from the Terraform Registry
- Configure module blocks with required and optional parameters
- Control which resources are created by modules
- Run Terraform init, plan, and apply commands with modules

## Prerequisites
- Basic understanding of Terraform syntax
- Familiarity with AWS IAM concepts
- Access to a Terraform environment with AWS provider configured

## Lesson Structure
This lesson consists of 11 progressive activities that build upon each other.

---

## Activity 1: Project Setup and Initial Inspection

### Objective
Inspect the initial Terraform configuration and understand the project structure.

### Instructions
1. Navigate to the project directory: `/root/terraform-projects/project-sapphire`
2. Examine the `main.tf` file to understand the initial configuration

### Expected Configuration
```hcl
module "iam_iam-user" {
  source  = "terraform-aws-modules/iam/aws//modules/iam-user"
  version = "5.28.0"
  # insert the 1 required variable here
}
```

### Key Observations
- The configuration uses a module block instead of a resource block
- The module is sourced from the Terraform Registry
- A specific version is pinned for reproducibility

---

## Activity 2: Understanding Module Configuration Blocks

### Question
**Which configuration block is defined in the main.tf file at the moment?**

### Answer
**Module block**

### Explanation
The configuration uses a `module` block, which is the standard way to call and configure modules in Terraform. Module blocks allow you to:
- Reference external modules
- Pass configuration parameters
- Version control module usage
- Reuse infrastructure code

---

## Activity 3: Understanding Module Sources

### Question
**What is the source of the module used in this configuration?**

### Answer
```hcl
source = "terraform-aws-modules/iam/aws//modules/iam-user"
```

### Explanation
The source points to the **public Terraform Registry**. The format follows:
- `terraform-aws-modules/iam/aws` - Organization/Namespace/Provider
- `//modules/iam-user` - Submodule path within the main module

### Terraform Registry Benefits
- Community-maintained modules
- Version control and documentation
- Quality assurance through community reviews
- Easy integration with `terraform init`

---

## Activity 4: Understanding Module Versions

### Question
**What is the version of the module used?**

### Answer
```hcl
version = "5.28.0"
```

### Explanation
Version pinning is crucial for:
- **Reproducibility**: Ensures consistent deployments
- **Stability**: Prevents unexpected changes from module updates
- **Security**: Allows time to review updates before applying
- **Rollback**: Easy to revert to previous versions if needed

### Best Practices
- Always pin module versions in production
- Use semantic versioning (major.minor.patch)
- Regularly update and test new versions

---

## Activity 5: Researching Module Requirements

### Question
**How many required arguments does this module expect?**

### Instructions
1. Visit the module documentation: https://registry.terraform.io/modules/terraform-aws-modules/iam/aws/latest/submodules/iam-user
2. Review the Inputs section to identify required parameters

### Answer
**1 required argument: `name`**

### Documentation Analysis
When researching modules, focus on:
- **Required vs Optional inputs**
- **Default values**
- **Input descriptions**
- **Usage examples**
- **Output values**

---

## Activity 6: Identifying Required Arguments

### Question
**Which argument is to be specified, just to create an IAM User with this module?**

### Answer
**`name`**

### Explanation
The `name` parameter is required because:
- IAM users must have unique names
- The module needs to know what to call the user
- It's used for resource identification and tagging

---

## Activity 7: Configuring the Module

### Objective
Update the module block to create an IAM user named "max" with only the required argument.

### Requirements
- Only use the module block in main.tf
- Module name: `iam_iam-user`
- Add only the single required argument
- User name: "max"

### Solution
```hcl
module "iam_iam-user" {
  source  = "terraform-aws-modules/iam/aws//modules/iam-user"
  version = "5.28.0"
  
  name = "max"
}
```

### Additional Files Added
The following files are now available in the configuration:

**provider.tf**
```hcl
terraform {
  required_providers {
    aws = {
      source = "hashicorp/aws"
      version = "5.11.0"
    }
  }
}

provider "aws" {
  region                      = var.region
  skip_credentials_validation = true
  skip_requesting_account_id  = true
  endpoints {
    iam = "http://aws:4566"
    ec2 = "http://aws:4566"
    s3 = "http://aws:4566"
  }
}
```

**variables.tf**
```hcl
variable "region" {
  default = "us-east-1"
}
```

### Next Steps
1. Run `terraform init` to download the module
2. Run `terraform plan` to see what will be created
3. Optionally run `terraform apply` to create resources

---

## Activity 8: Analyzing the Execution Plan

### Question
**How many resources are set to be created in the execution plan?**

### Answer
**Plan: 3 to add, 0 to change, 0 to destroy.**

### Understanding the Plan Output
The plan shows:
- **3 resources** will be created
- **0 changes** to existing resources
- **0 resources** will be destroyed

This indicates a fresh deployment with no existing state.

---

## Activity 9: Identifying Resources to be Created

### Question
**Which resources are set to be created?**

### Answer
```hcl
# module.iam_iam-user.aws_iam_access_key.this_no_pgp[0] will be created
# module.iam_iam-user.aws_iam_user.this[0] will be created
# module.iam_iam-user.aws_iam_user_login_profile.this[0] will be created
```

### Resource Breakdown
1. **aws_iam_user**: The main IAM user resource
2. **aws_iam_access_key**: Access key for programmatic access
3. **aws_iam_user_login_profile**: Login profile for AWS console access

### Module Behavior
Even though we only specified the `name` parameter, the module creates additional resources by default.

---

## Activity 10: Understanding Default Module Behavior

### Question
**Why is the module creating additional resources, when only the name for creating an IAM User was defined in the main.tf file?**

### Answer
**Resources will be created by default as per module configuration**

### Explanation
Modules often create multiple related resources by default because:
- **Convenience**: Most users want the complete functionality
- **Best Practices**: Includes security and access patterns
- **Flexibility**: Can be disabled through configuration parameters

### Key Learning Point
Always review module documentation to understand:
- What resources are created by default
- Which parameters control resource creation
- How to customize the module behavior

---

## Activity 11: Controlling Resource Creation

### Objective
Update the module to create only the IAM user, disabling access key and login profile creation.

### Requirements
- Create only the IAM user
- Disable `create_iam_access_key`
- Disable `create_iam_user_login_profile`

### Solution
```hcl
module "iam_iam-user" {
  source  = "terraform-aws-modules/iam/aws//modules/iam-user"
  version = "5.28.0"
  
  name = "max"

  # Explicitly create the IAM user. This is the default behavior,
  # but setting it to 'true' makes the intent clear.
  create_user = true

  # Set to 'false' to disable the creation of an IAM access key.
  create_iam_access_key = false

  # Set to 'false' to disable the creation of a login profile for the user.
  create_iam_user_login_profile = false
}
```

### Updated Plan Output
```
Plan: 1 to add, 0 to change, 0 to destroy.
```

### Execution Results
```bash
Do you want to perform these actions?
  Terraform will perform the actions described above.
  Only 'yes' will be accepted to approve.

  Enter a value: yes

module.iam_iam-user.aws_iam_user.this[0]: Creating...
module.iam_iam-user.aws_iam_user.this[0]: Creation complete after 0s [id=max]

Apply complete! Resources: 1 added, 0 changed, 0 destroyed.
```

### Key Achievements
- Successfully created only the IAM user
- Controlled module behavior through parameters
- Reduced resource count from 3 to 1
- Applied infrastructure changes successfully

---

## Key Takeaways

### Module Fundamentals
1. **Modules are reusable infrastructure components** that encapsulate resources and logic
2. **Terraform Registry** provides community-maintained modules
3. **Version pinning** ensures reproducible deployments
4. **Module parameters** control behavior and resource creation

### Best Practices
1. **Always read module documentation** before using
2. **Pin module versions** in production environments
3. **Understand default behavior** and customize as needed
4. **Use descriptive module names** for clarity
5. **Test modules** in development before production use

### Common Module Parameters
- **create_*** parameters: Control resource creation
- **enable_*** parameters: Enable/disable features
- **name**: Often required for resource identification
- **tags**: Add metadata to resources

### Troubleshooting Tips
1. **Check module documentation** for parameter requirements
2. **Review terraform plan** to understand what will be created
3. **Use terraform validate** to check syntax
4. **Check terraform init** output for module download issues

---

## Additional Resources

### Documentation Links
- [Terraform Modules Documentation](https://developer.hashicorp.com/terraform/language/modules)
- [Terraform Registry](https://registry.terraform.io/)
- [AWS IAM Module Documentation](https://registry.terraform.io/modules/terraform-aws-modules/iam/aws/latest)

### Related Concepts
- **Module Composition**: Using multiple modules together
- **Local Modules**: Creating your own modules
- **Module Versioning**: Managing module updates
- **Module Testing**: Validating module functionality

### Next Steps
1. Practice with other AWS modules (EC2, S3, VPC)
2. Learn to create custom modules
3. Explore module composition patterns
4. Study advanced module features (count, for_each, depends_on)

---

## Exercise Questions

### Review Questions
1. What is the difference between a module and a resource in Terraform?
2. Why is it important to pin module versions?
3. How can you control which resources a module creates?
4. What information should you look for in module documentation?

### Practice Exercises
1. Create an IAM user with a custom access key policy
2. Use a different version of the IAM module
3. Create multiple IAM users using the same module
4. Research and use a different AWS module (e.g., EC2, S3)

### Challenge Questions
1. How would you create 5 IAM users with different names using a single module?
2. What would happen if you removed the version constraint from the module?
3. How can you pass variables from your main configuration to a module?

---

*This guide provides a comprehensive foundation for understanding and working with Terraform modules. Practice these concepts and explore additional modules to build your expertise.*
