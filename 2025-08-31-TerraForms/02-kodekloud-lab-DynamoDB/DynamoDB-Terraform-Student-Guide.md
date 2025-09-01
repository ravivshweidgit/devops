# Terraform AWS DynamoDB Lab - Student Guide

## Overview
This lab will teach you how to work with Amazon DynamoDB tables using Terraform. You'll learn to create, configure, and populate DynamoDB tables through infrastructure as code.

**Lab Environment**: KodeKloud Learning Platform  
**Duration**: Approximately 30-45 minutes  
**Prerequisites**: Basic understanding of Terraform and AWS DynamoDB concepts

---

## Table of Contents
1. [Lab Setup](#lab-setup)
2. [Exercise 1: Troubleshooting DynamoDB Configuration](#exercise-1-troubleshooting-dynamodb-configuration)
3. [Exercise 2: Fixing Primary Key Configuration](#exercise-2-fixing-primary-key-configuration)
4. [Exercise 3: Understanding Table Structure](#exercise-3-understanding-table-structure)
5. [Exercise 4: Working with Global Secondary Indexes](#exercise-4-working-with-global-secondary-indexes)
6. [Exercise 5: Adding Data to DynamoDB Tables](#exercise-5-adding-data-to-dynamodb-tables)
7. [Key Concepts](#key-concepts)
8. [Troubleshooting Tips](#troubleshooting-tips)

---

## Lab Setup

### Initial Configuration
The lab environment has been pre-configured with the following directory structure:
```
/root/terraform-projects/DynamoDB/
├── project-sapphire-user-data/
└── project-sapphire-inventory/
```

### Prerequisites Check
Before starting, ensure you have:
- Access to the KodeKloud lab environment
- AWS credentials configured
- Terraform installed and accessible

---

## Exercise 1: Troubleshooting DynamoDB Configuration

### Objective
Identify and understand common DynamoDB configuration errors in Terraform.

### Step 1: Navigate to the Project Directory
```bash
cd /root/terraform-projects/DynamoDB/project-sapphire-user-data/
```

### Step 2: Examine the Initial Configuration
The file `main.tf` contains the following configuration:

```hcl
resource "aws_dynamodb_table" "project_sapphire_user_data" {
  name           = "userdata"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "UserId"

  attribute {
    name = "Name"
    type = "S"
  }
}
```

### Step 3: Run Terraform Plan
```bash
terraform plan
```

### Expected Error
You should encounter the following error:
```
Error: 2 errors occurred:
      * all attributes must be indexed. Unused attributes: ["Name"]
      * all indexes must match a defined attribute. Unmatched indexes: ["UserId"]
```

### Understanding the Error
The error occurs because:
1. **Missing Primary Key Attribute**: The `hash_key` references "UserId", but no attribute named "UserId" is defined
2. **Unused Attribute**: The "Name" attribute is defined but not used as a key

**Key Learning**: Every DynamoDB table must have its primary key (hash key) defined as an attribute.

---

## Exercise 2: Fixing Primary Key Configuration

### Objective
Fix the DynamoDB table configuration by properly defining the primary key attribute.

### Step 1: Update the Configuration
Modify the `main.tf` file to include the missing UserId attribute:

```hcl
resource "aws_dynamodb_table" "project_sapphire_user_data" {
  name           = "userdata"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "UserId"

  attribute {
    name = "UserId"
    type = "N"  # Number type for UserId
  }
  
  attribute {
    name = "Name"
    type = "S"
  }
}
```

### Step 2: Initialize and Apply
```bash
terraform init
terraform plan
terraform apply
```

### Expected Output
```
aws_dynamodb_table.project_sapphire_user_data: Creating...
aws_dynamodb_table.project_sapphire_user_data: Creation complete after 9s [id=userdata]

Apply complete! Resources: 1 added, 0 changed, 0 destroyed.
```

### Key Points
- **Primary Key Requirement**: The hash key must always be defined as an attribute
- **Data Types**: Use "N" for numbers, "S" for strings, "B" for booleans
- **Billing Mode**: PAY_PER_REQUEST means you pay only for what you use

---

## Exercise 3: Understanding Table Structure

### Objective
Analyze a more complex DynamoDB table configuration with multiple attributes and indexes.

### Step 1: Navigate to Inventory Project
```bash
cd /root/terraform-projects/DynamoDB/project-sapphire-inventory/
```

### Step 2: Examine the Configuration
Review the `main.tf` file:

```hcl
resource "aws_dynamodb_table" "project_sapphire_inventory" {
  name           = "inventory"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "AssetID"

  attribute {
    name = "AssetID"
    type = "N"
  }
  attribute {
    name = "AssetName"
    type = "S"
  }
  attribute {
    name = "age"
    type = "N"
  }
  attribute {
    name = "Hardware"
    type = "B"
  }
  
  global_secondary_index {
    name             = "AssetName"
    hash_key         = "AssetName"
    projection_type  = "ALL"
  }
  global_secondary_index {
    name             = "age"
    hash_key         = "age"
    projection_type  = "ALL"
  }
  global_secondary_index {
    name             = "Hardware"
    hash_key         = "Hardware"
    projection_type  = "ALL"
  }
}
```

### Step 3: Answer Key Questions

**Question 1**: What is the name of the DynamoDB table resource?
**Answer**: `project_sapphire_inventory`

**Question 2**: What is the name of the DynamoDB Table that is created?
**Answer**: `inventory`

**Question 3**: How many attributes are defined in this table?
**Answer**: `4` (AssetID, AssetName, age, Hardware)

**Question 4**: What is the name and type of the Primary Key?
**Answer**: `AssetID`, `Number`

---

## Exercise 4: Working with Global Secondary Indexes

### Objective
Understand how Global Secondary Indexes (GSI) work in DynamoDB and their configuration in Terraform.

### GSI Configuration Analysis
The table has three Global Secondary Indexes:

1. **AssetName Index**
   - Hash Key: AssetName
   - Projection Type: ALL
   - Purpose: Query by asset name

2. **Age Index**
   - Hash Key: age
   - Projection Type: ALL
   - Purpose: Query by age

3. **Hardware Index**
   - Hash Key: Hardware
   - Projection Type: ALL
   - Purpose: Query by hardware status

### Key Concepts
- **Projection Type**: ALL means all attributes are copied to the index
- **Hash Key**: The attribute used for partitioning in the index
- **Performance**: GSIs enable efficient queries on non-primary key attributes

---

## Exercise 5: Adding Data to DynamoDB Tables

### Objective
Learn how to populate DynamoDB tables with data using Terraform.

### Step 1: Add Item Configuration
Add the following resource to your `main.tf` file:

```hcl
resource "aws_dynamodb_table_item" "upload" {
  table_name = aws_dynamodb_table.project_sapphire_inventory.name
  hash_key   = aws_dynamodb_table.project_sapphire_inventory.hash_key
 
  item = jsonencode({
    AssetID = {
      N = "1"
    }
    AssetName = {
      S = "printer"
    }
    age = {
      N = "5"
    }
    Hardware = {
      B = "true"
    }
  })
}
```

### Step 2: Apply the Configuration
```bash
terraform apply
```

### Expected Output
```
aws_dynamodb_table_item.upload: Creating...
aws_dynamodb_table_item.upload: Creation complete after 0s [id=inventory|AssetID|||1]

Apply complete! Resources: 1 added, 0 changed, 0 destroyed.
```

### Key Learning Points
- **Resource References**: Use `aws_dynamodb_table.project_sapphire_inventory.name` to reference the table name
- **Hash Key Reference**: Use `aws_dynamodb_table.project_sapphire_inventory.hash_key` to reference the primary key
- **JSON Encoding**: Use `jsonencode()` to format the item data
- **Data Types**: DynamoDB requires explicit type declarations (N, S, B)

---

## Key Concepts

### DynamoDB Table Components

1. **Primary Key (Hash Key)**
   - Must be defined as an attribute
   - Used for partitioning data
   - Required for all DynamoDB tables

2. **Attributes**
   - Define the structure of your data
   - Types: String (S), Number (N), Boolean (B), Binary, etc.
   - All attributes used in keys must be defined

3. **Global Secondary Indexes (GSI)**
   - Enable efficient queries on non-primary key attributes
   - Can have different hash keys than the main table
   - Projection types: ALL, KEYS_ONLY, INCLUDE

4. **Billing Modes**
   - **PAY_PER_REQUEST**: Pay only for what you use (on-demand)
   - **PROVISIONED**: Pre-allocate read/write capacity units

### Terraform Resources

1. **aws_dynamodb_table**
   - Creates the DynamoDB table
   - Defines structure, indexes, and configuration

2. **aws_dynamodb_table_item**
   - Adds individual items to the table
   - Uses JSON encoding for data formatting
   - References table name and hash key

---

## Troubleshooting Tips

### Common Errors and Solutions

1. **"all indexes must match a defined attribute"**
   - **Cause**: Hash key references an undefined attribute
   - **Solution**: Add the missing attribute definition

2. **"all attributes must be indexed"**
   - **Cause**: Attribute defined but not used in any key
   - **Solution**: Either use the attribute in a key or remove it

3. **JSON encoding errors**
   - **Cause**: Incorrect data type format
   - **Solution**: Ensure proper DynamoDB type notation (N, S, B)

4. **Reference errors**
   - **Cause**: Incorrect resource references
   - **Solution**: Use proper Terraform reference syntax

### Best Practices

1. **Always define primary key attributes**
2. **Use meaningful attribute names**
3. **Choose appropriate data types**
4. **Plan before applying changes**
5. **Use resource references for consistency**

---

## Lab Completion Checklist

- [ ] Successfully identified and fixed DynamoDB configuration errors
- [ ] Created a DynamoDB table with proper primary key configuration
- [ ] Analyzed table structure with multiple attributes
- [ ] Understood Global Secondary Index configuration
- [ ] Added data to DynamoDB table using Terraform
- [ ] Verified all resources were created successfully

---

## Additional Resources

- [AWS DynamoDB Documentation](https://docs.aws.amazon.com/dynamodb/)
- [Terraform AWS Provider Documentation](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [DynamoDB Data Types](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/HowItWorks.NamingRulesDataTypes.html)

---

## Next Steps

After completing this lab, consider exploring:
- Composite keys (hash + range keys)
- Local Secondary Indexes
- DynamoDB Streams
- Advanced query patterns
- Performance optimization techniques

---

*This lab provides hands-on experience with Terraform and AWS DynamoDB, building a solid foundation for infrastructure as code practices with NoSQL databases.*
