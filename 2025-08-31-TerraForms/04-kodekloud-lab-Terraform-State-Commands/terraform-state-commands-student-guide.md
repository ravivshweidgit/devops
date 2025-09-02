# Terraform State Commands - Student Guide

## Overview
This guide covers the essential Terraform state commands and concepts through hands-on practice with the KodeKloud Terraform for Beginners lab. You'll learn how to inspect, manage, and manipulate Terraform state files using various commands.

## Prerequisites
- Basic understanding of Terraform configuration files
- Access to the KodeKloud lab environment
- Familiarity with local file and random_pet resources

## Learning Objectives
By the end of this lesson, you will be able to:
- List and inspect resources in Terraform state
- Show detailed attributes of specific resources
- Remove resources from state management
- Work with remote state backends
- Rename resources in both configuration and state
- Understand the difference between local and remote state

## Lab Environment Setup
The lesson uses two project directories:
- `/root/terraform-projects/project-anime` - Contains local file resources
- `/root/terraform-projects/super-pets` - Contains random_pet resources with remote state

## Exercise 1: Inspecting Terraform State

### Scenario
Navigate to the anime project directory and inspect the existing resources.

```bash
cd /root/terraform-projects/project-anime
```

### Configuration Files
The project contains a `main.tf` file with four local file resources:

```hcl
resource "local_file" "top10" {
    filename = "/root/anime/top10.txt"
    content  = "1. Naruto\n2. DragonBallZ\n3. Death Note\nFullmetal Alchemist\nOne-Punch Man\n"
}

resource "local_file" "hall_of_fame" {
  filename = "/root/anime/hall-of-fame.txt"
  content = "1.Attack On Titan\n2. Naruto\n3. Bleach\n"
}

resource "local_file" "new_shows" {
  filename = "/root/anime/new_shows.txt"
  content = "1. Cannon Busters\n2. Last Hope\n3. Lost Song\n"
}

resource "local_file" "classics" {
  filename = "/root/anime/classic_shows.txt"
  content = "1. DragonBall\n"
}
```

### Task: List Resources in State
**Command:** `terraform state list`

**Expected Output:**
```
local_file.classics
local_file.hall_of_fame
local_file.new_shows
local_file.top10
```

**Key Learning:** The `terraform state list` command shows all resources currently managed by Terraform in the state file.

**Question:** Which resource names are NOT part of the terraform state?
**Answer:** `super_pets` is not a resource (it's not defined in the configuration).

---

## Exercise 2: Inspecting Resource Attributes

### Task: Show Resource Details
**Command:** `terraform state show local_file.classics`

**Expected Output:**
```hcl
# local_file.classics:
resource "local_file" "classics" {
    content              = <<-EOT
        1. DragonBall
    EOT
    content_base64sha256 = "6Ity8EEWB9hY2pJUjJQsdyBi7iDtrqnHg7E0VR9KS4A="
    content_base64sha512 = "lRKrxM4reT5okTZxIy6k/HdgLiXIJ+L1LIr2FUWcLldv44rFq/kOmiB6qOO0ny3Yl6w6C+79BdTy3TLHG0G5fg=="
    content_md5          = "13d46e58bee23e8d0560d9cf3cef8966"
    content_sha1         = "69f539876d8db4e6873466ab5b4d56ebf32667b2"
    content_sha256       = "e88b72f0411607d858da92548c942c772062ee20edaea9c783b134551f4a4b80"
    content_sha512       = "9512abc4ce2b793e68913671232ea4fc77602e25c827e2f52c8af615459c2e576fe38ac5abf90e9a207aa8e3b49f2dd897ac3a0beefd05d4f2dd32c71b41b97e"
    directory_permission = "0777"
    file_permission      = "0777"
    filename             = "/root/anime/classic_shows.txt"
    id                   = "69f539876d8db4e6873466ab5b4d56ebf32667b2"
}
```

**Key Learning:** The `terraform state show` command displays detailed information about a specific resource, including computed attributes like hashes and IDs.

---

## Exercise 3: Finding Resource IDs

### Task: Extract Resource ID
**Command:** `terraform state show local_file.top10 | grep id`

**Expected Output:**
```
    id                   = "a96174702c7d532583e312e123a216e35721021f"
```

**Alternative Command:** `terraform state pull | jq '.resources[] | select(.name == "top10").instances[0].attributes.id'`

**Expected Output:**
```
"a96174702c7d532583e312e123a216e35721021f"
```

**Key Learning:** Resource IDs are unique identifiers that Terraform assigns to each resource. They can be extracted using grep or JSON processing tools.

---

## Exercise 4: Removing Resources from State

### Task: Remove Resource Management
**Command:** `terraform state rm local_file.hall_of_fame`

**Expected Output:**
```
Removed local_file.hall_of_fame
Successfully removed 1 resource instance(s).
```

**Key Learning:** The `terraform state rm` command removes a resource from Terraform's state management without destroying the actual resource. This is useful when you want to stop managing a resource that was previously created by Terraform.

**Important Note:** The physical file remains on disk, but Terraform will no longer track or manage it.

---

## Exercise 5: Working with Different Resource Types

### Task: Inspect Super-Pets Project
**Command:** `cd ../super-pets/`

**Command:** `terraform state list`

**Expected Output:**
```
random_pet.super_pet_1
random_pet.super_pet_2
```

**Key Learning:** Different projects can use different resource types. This project uses `random_pet` resources instead of `local_file` resources.

---

## Exercise 6: Understanding Remote State

### Task: Investigate Missing State File
**Observation:** No `terraform.tfstate` file is present, yet state commands work.

**Configuration:**
```hcl
terraform {
  backend "s3" {
    key = "terraform.tfstate"
    region = "us-east-1"
    bucket = "remote-state"
    endpoint = "http://172.16.238.105:9000"
    force_path_style = true
    skip_credentials_validation = true
    skip_metadata_api_check = true
    skip_region_validation = true
  }
}
```

**Answer:** The state is stored remotely in an S3-compatible backend (MinIO in this case).

**Key Learning:** Remote state backends store state files in external storage systems, making them accessible to multiple team members and providing better security and collaboration features.

---

## Exercise 7: Working with Remote State

### Task: Find Resource ID in Remote State
**Command:** `terraform state show random_pet.super_pet_2 | grep id`

**Expected Output:**
```
    id        = "Wonder-smart-gull"
```

**Alternative Command:** `terraform state pull | jq '.resources[] | select(.name == "super_pet_2").instances[0].attributes.id'`

**Expected Output:**
```
"Wonder-smart-gull"
```

**Key Learning:** State commands work the same way regardless of whether the state is stored locally or remotely.

---

## Exercise 8: Renaming Resources

### Task: Rename Resource in Both Configuration and State

#### Step 1: Update Configuration File
Edit `main.tf` to change the resource name:

```hcl
# Before
resource "random_pet" "super_pet_1" {
    length = var.length1
    prefix = var.prefix1
}

# After
resource "random_pet" "ultra_pet" {
    length = var.length1
    prefix = var.prefix1
}
```

#### Step 2: Update State
**Command:** `terraform state mv random_pet.super_pet_1 random_pet.ultra_pet`

**Expected Output:**
```
Move "random_pet.super_pet_1" to "random_pet.ultra_pet"
Successfully moved 1 object(s).
```

**Key Learning:** The `terraform state mv` command renames resources in the state file. This is useful when you want to refactor your configuration without destroying and recreating resources.

**Important:** Always update both the configuration file and the state when renaming resources.

---

## Summary of Terraform State Commands

| Command | Purpose | Example |
|---------|---------|---------|
| `terraform state list` | List all resources in state | `terraform state list` |
| `terraform state show` | Show details of a specific resource | `terraform state show local_file.classics` |
| `terraform state rm` | Remove resource from state management | `terraform state rm local_file.hall_of_fame` |
| `terraform state mv` | Rename/move resources in state | `terraform state mv old_name new_name` |
| `terraform state pull` | Download remote state | `terraform state pull` |

## Key Concepts

### 1. State Management
- Terraform state tracks the current state of your infrastructure
- State can be stored locally or remotely
- State commands allow you to inspect and manipulate this information

### 2. Local vs Remote State
- **Local state:** Stored in `terraform.tfstate` file
- **Remote state:** Stored in external backends (S3, Consul, etc.)
- Remote state enables team collaboration and better security

### 3. Resource Lifecycle
- Resources can be added, removed, or renamed in state
- Removing from state doesn't destroy the actual resource
- Renaming requires updates to both configuration and state

### 4. State Inspection
- Use `terraform state show` to examine resource attributes
- Resource IDs are unique identifiers for each resource
- State can be exported as JSON for programmatic access

## Best Practices

1. **Always backup state files** before making changes
2. **Use remote state** for production environments
3. **Test state commands** in non-production environments first
4. **Document state changes** for team awareness
5. **Use meaningful resource names** to avoid frequent renaming

## Common Use Cases

- **Resource cleanup:** Remove resources from Terraform management
- **Configuration refactoring:** Rename resources without recreation
- **Troubleshooting:** Inspect resource attributes and relationships
- **State migration:** Move between different state backends
- **Team collaboration:** Share state information across team members

## Next Steps

After completing this lesson, you should:
1. Practice these commands in your own Terraform projects
2. Explore additional state commands like `terraform state pull` and `terraform state push`
3. Learn about state locking and concurrency control
4. Understand how to handle state conflicts in team environments

## Additional Resources

- [Terraform State Documentation](https://www.terraform.io/docs/language/state/index.html)
- [Terraform State Commands Reference](https://www.terraform.io/docs/cli/commands/state/index.html)
- [Remote State Backends](https://www.terraform.io/docs/language/settings/backends/index.html)
- [State File Format](https://www.terraform.io/docs/language/state/index.html#state-file-format)
