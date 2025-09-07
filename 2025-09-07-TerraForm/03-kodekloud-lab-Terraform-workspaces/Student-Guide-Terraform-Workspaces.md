# Terraform Workspaces - Student Guide

## Overview
This guide covers the fundamentals of Terraform workspaces, a powerful feature that allows you to manage multiple environments (like development, staging, and production) using the same Terraform configuration. This lesson is part of the [Kodekloud Terraform for Beginners course](https://learn.kodekloud.com/user/courses/udemy-labs-terraform-for-beginners).

## Learning Objectives
By the end of this lesson, you will be able to:
- Understand what Terraform workspaces are and their purpose
- Create and manage multiple workspaces
- Switch between different workspaces
- Understand how workspace state files are organized
- Use workspace-specific variables in your Terraform configurations
- Deploy resources across multiple environments using workspaces

## Prerequisites
- Basic understanding of Terraform
- Access to a Linux environment with Terraform installed
- AWS CLI configured (for the practical examples)

## Lesson Structure
This lesson consists of 11 hands-on exercises that will guide you through working with Terraform workspaces.

---

## Exercise 1: Understanding Default Workspace

### Question
When we start off and create a configuration in terraform, what is the workspace that is created, to begin with?

### Answer
**default workspace**

### Explanation
When you initialize a new Terraform configuration, Terraform automatically creates a workspace called "default". This is the workspace you work in unless you explicitly create and switch to other workspaces.

---

## Exercise 2: Listing Existing Workspaces

### Task
Navigate to the configuration directory `/root/terraform-projects/project-sapphire`. We have a few configuration files already created here. How many workspaces are created for this configuration currently?

### Solution
```bash
terraform workspace list
```

### Output
```
* default
```

### Explanation
- The `terraform workspace list` command shows all available workspaces
- The asterisk (*) indicates the currently active workspace
- Initially, only the default workspace exists

---

## Exercise 3: Creating New Workspaces

### Task
Create three new workspaces called `us-payroll`, `uk-payroll` and `india-payroll`.

### Solution

#### Create us-payroll workspace:
```bash
terraform workspace new us-payroll
```

**Output:**
```
Created and switched to workspace "us-payroll"!

You're now on a new, empty workspace. Workspaces isolate their state,
so if you run "terraform plan" Terraform will not see any existing state
for this configuration.
```

#### Create uk-payroll workspace:
```bash
terraform workspace new uk-payroll
```

**Output:**
```
Created and switched to workspace "uk-payroll"!

You're now on a new, empty workspace. Workspaces isolate their state,
so if you run "terraform plan" Terraform will not see any existing state
for this configuration.
```

#### Create india-payroll workspace:
```bash
terraform workspace new india-payroll
```

**Output:**
```
Created and switched to workspace "india-payroll"!

You're now on a new, empty workspace. Workspaces isolate their state,
so if you run "terraform plan" Terraform will not see any existing state
for this configuration.
```

### Key Points
- Each workspace has its own isolated state
- When you create a new workspace, you automatically switch to it
- The prompt shows the current workspace (e.g., `via 💠 us-payroll`)

---

## Exercise 4: Switching Between Workspaces

### Task
Now, switch to the workspace called `us-payroll`.

### Solution
```bash
terraform workspace select us-payroll
```

### Output
```
Switched to workspace "us-payroll".
```

### Explanation
- Use `terraform workspace select <workspace-name>` to switch between workspaces
- You can verify the current workspace using `terraform workspace list`

---

## Exercise 5: Understanding Workspace State Storage

### Question
Where would the state file for the workspace called `india-payroll` be stored?

### Answer
**`terraform.tfstate.d/india-payroll`**

### Verification
```bash
pwd
/root/terraform-projects/project-sapphire/terraform.tfstate.d/india-payroll
```

### Explanation
- Each workspace has its own state file stored in the `terraform.tfstate.d/` directory
- The directory structure is: `terraform.tfstate.d/<workspace-name>/`
- This isolation ensures that changes in one workspace don't affect others

---

## Exercise 6: Module Integration

### Task
Let's now write the main.tf file to make use of the same module that we saw in the terraform modules lecture. The project-sapphire configuration directory will be used to deploy the same payroll application stack in different regions. The module is located at the path `/root/terraform-projects/modules/payroll-app`.

### Explanation
This exercise sets up the foundation for using a reusable module across different workspaces, allowing us to deploy the same infrastructure in different regions.

---

## Exercise 7: Understanding Variable Types

### Task
Inside the configuration directory, we have already added the variables.tf and the provider.tf file. Inspect them. What type of variable is `region`?

### Answer
**map**

### Variable Definition
```hcl
variable "region" {
    type = map
    default = {
        "us-payroll" = "us-east-1"
        "uk-payroll" = "eu-west-2"
        "india-payroll" = "ap-south-1"
    }
}
```

### Explanation
- The `region` variable is of type `map`
- Maps allow you to store key-value pairs
- In this case, each workspace name maps to its corresponding AWS region

---

## Exercise 8: Working with Map Values

### Question
What is the default value of the key called `india-payroll` for the variable `region`?

### Answer
**`"ap-south-1"`**

### Explanation
- Maps use the syntax `"key" = "value"`
- For the key `"india-payroll"`, the corresponding value is `"ap-south-1"`
- This represents the AWS Asia Pacific (Mumbai) region

---

## Exercise 9: AMI Variable Configuration

### Question
What is the default value of the key called `india-payroll` for the variable `ami`?

### Answer
**`"ami-55140119877avm"`**

### Variable Definition
```hcl
variable "ami" {
    type = map
    default = {
        "us-payroll" = "ami-24e140119877avm"
        "uk-payroll" = "ami-35e140119877avm"
        "india-payroll" = "ami-55140119877avm"
    }
}
```

### Explanation
- Each workspace has its own AMI (Amazon Machine Image) ID
- Different regions require different AMI IDs
- This ensures the correct image is used for each deployment

---

## Exercise 10: Creating the Main Configuration

### Task
Now, update the main.tf of the root module to call the child module located at `/root/terraform-projects/modules/payroll-app`. Adhere to the following specifications:

- **Module name:** `payroll_app`
- **This module expects two mandatory arguments:**
  - `app_region` - use the values from variable called `region`
  - `ami` - use the values from the variable called `ami`
- The values for these two arguments should be selected based on the workspace you are on.

### Solution
```hcl
main.tf
module "payroll_app" {
  source = "/root/terraform-projects/modules/payroll-app"

  app_region = lookup(var.region, terraform.workspace)

  ami = lookup(var.ami, terraform.workspace)
}
```

### Key Concepts

#### The `lookup()` Function
- `lookup(map, key, default)` retrieves a value from a map using a key
- `terraform.workspace` is a built-in variable that contains the current workspace name
- This allows dynamic selection of values based on the current workspace

#### Workspace-Specific Values
- **us-payroll workspace:** `app_region = "us-east-1"`, `ami = "ami-24e140119877avm"`
- **uk-payroll workspace:** `app_region = "eu-west-2"`, `ami = "ami-35e140119877avm"`
- **india-payroll workspace:** `app_region = "ap-south-1"`, `ami = "ami-55140119877avm"`

### Next Steps
Once ready, run `terraform init`. You don't have to create (apply) the resources yet!

---

## Exercise 11: Deploying Across All Workspaces

### Task
Now, using the same configuration, create the resources on all three workspaces that you created earlier!

### Solution

#### Step 1: Verify available workspaces
```bash
terraform workspace list
```

**Output:**
```
  default
  india-payroll
  uk-payroll
* us-payroll
```

#### Step 2: Deploy to india-payroll workspace
```bash
terraform workspace select india-payroll
terraform apply
```

#### Step 3: Deploy to uk-payroll workspace
```bash
terraform workspace select uk-payroll
terraform apply
```

### Sample Apply Output
```
module.payroll_app.aws_s3_bucket.payroll_data: Creating...
module.payroll_app.aws_dynamodb_table.payroll_db: Creating...
module.payroll_app.aws_s3_bucket.payroll_data: Creation complete after 0s [id=us-east-1-flexit-payroll-alpha-22001c]
module.payroll_app.aws_dynamodb_table.payroll_db: Creation complete after 6s [id=us-east-1_user_data]
module.payroll_app.aws_instance.app_server: Creating...
module.payroll_app.aws_instance.app_server: Still creating... [10s elapsed]
module.payroll_app.aws_instance.app_server: Creation complete after 10s [id=i-2b048e728c8b39248]

Apply complete! Resources: 3 added, 0 changed, 0 destroyed.
```

### Explanation
- Each workspace deployment creates resources in its respective region
- The same configuration is reused across all workspaces
- State files are completely isolated between workspaces

---

## Key Takeaways

### Benefits of Terraform Workspaces
1. **Environment Isolation:** Each workspace maintains its own state
2. **Code Reusability:** Same configuration can be used across multiple environments
3. **Easy Management:** Simple commands to switch between environments
4. **Cost Efficiency:** No need to duplicate configuration files

### Best Practices
1. **Naming Convention:** Use descriptive workspace names (e.g., `dev`, `staging`, `prod`)
2. **Variable Management:** Use maps to define environment-specific values
3. **State Management:** Always verify which workspace you're in before making changes
4. **Documentation:** Document workspace-specific configurations

### Common Commands
```bash
# List all workspaces
terraform workspace list

# Create a new workspace
terraform workspace new <workspace-name>

# Switch to a workspace
terraform workspace select <workspace-name>

# Show current workspace
terraform workspace show

# Delete a workspace (be careful!)
terraform workspace delete <workspace-name>
```

### Built-in Variables
- `terraform.workspace`: Contains the name of the current workspace
- Use this variable to dynamically select values based on the current workspace

---

## Troubleshooting

### Common Issues
1. **Wrong Workspace:** Always check which workspace you're in before applying changes
2. **State Conflicts:** Each workspace has isolated state, so no conflicts between workspaces
3. **Variable Lookup Errors:** Ensure the workspace name matches the keys in your variable maps

### Verification Steps
1. Run `terraform workspace list` to see all workspaces
2. Check the current workspace with `terraform workspace show`
3. Verify variable values with `terraform console` and test lookups

---

## Conclusion

Terraform workspaces provide a powerful way to manage multiple environments using the same configuration. By understanding how to create, switch between, and use workspaces effectively, you can streamline your infrastructure management across different environments while maintaining proper isolation and organization.

This lesson demonstrated how to:
- Create and manage multiple workspaces
- Use workspace-specific variables with the `lookup()` function
- Deploy the same infrastructure across different regions
- Maintain isolated state files for each environment

Continue practicing with workspaces to become comfortable with this essential Terraform feature!
