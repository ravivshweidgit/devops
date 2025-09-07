# Terraform Functions and Conditional Expressions - Student Guide

## Overview
This lab focuses on Terraform functions and conditional expressions, essential tools for dynamic infrastructure configuration. You'll learn to manipulate data, work with different variable types, and create conditional logic in your Terraform configurations.

**Course Reference:** [Kodekloud Terraform for Beginners](https://learn.kodekloud.com/user/courses/udemy-labs-terraform-for-beginners)

## Learning Objectives
By the end of this lab, you will be able to:
- Use Terraform built-in functions for data manipulation
- Work with different variable types (string, list, set)
- Implement conditional expressions for dynamic resource configuration
- Use meta-arguments like `count` and `for_each` effectively
- Navigate and test functions using the Terraform console

## Prerequisites
- Basic understanding of Terraform syntax
- Access to AWS CLI configured
- Terraform installed and configured

---

## Part 1: Understanding Terraform Functions

### Exercise 1: Basic Function Testing
**Objective:** Test basic Terraform functions using the console

#### Step 1: Test the `floor()` function
```bash
terraform console
```
```hcl
> floor(10.9)
10
```
**Explanation:** The `floor()` function returns the largest integer less than or equal to the given number.

#### Step 2: Test the `title()` function
```hcl
> title("user-generated password file")
"User-generated Password File"
```
**Explanation:** The `title()` function converts the first letter of each word to uppercase.

#### Step 3: Understanding the `lookup()` function
**Question:** Which type of variable does the `lookup()` function work with?
**Answer:** Map

**Explanation:** The `lookup()` function retrieves values from maps using keys.

---

## Part 2: Working with String Variables and Lists

### Exercise 2: Converting Strings to Lists
**Objective:** Convert a colon-separated string to a list and create multiple IAM users

#### Step 1: Navigate to the project directory
```bash
cd /root/terraform-projects/project-sonic
```

#### Step 2: Examine the variables
Check the `variables.tf` file:
```hcl
variable "cloud_users" {
    type = string
    default = "andrew:ken:faraz:mutsumi:peter:steve:braja"
}
```

**Question:** What type of variable is `cloud_users`?
**Answer:** string

#### Step 3: Create IAM users using the `split()` function
Add the following resource to `main.tf`:

```hcl
resource "aws_iam_user" "cloud" {
  count = length(split(":", var.cloud_users))
  name = split(":", var.cloud_users)[count.index]
}
```

**Key Concepts:**
- `split(":", var.cloud_users)`: Converts the string to a list by splitting on ":"
- `length()`: Returns the number of elements in the list
- `count.index`: Provides the current index in the count loop
- `[count.index]`: Accesses the specific element at that index

#### Step 4: Apply the configuration
```bash
terraform init
terraform plan
terraform apply
```

**Expected Output:**
```
aws_iam_user.cloud[0]: Creating...
aws_iam_user.cloud[4]: Creating...
aws_iam_user.cloud[5]: Creating...
aws_iam_user.cloud[1]: Creating...
aws_iam_user.cloud[3]: Creating...
aws_iam_user.cloud[6]: Creating...
aws_iam_user.cloud[2]: Creating...
aws_iam_user.cloud[0]: Creation complete after 0s [id=andrew]
aws_iam_user.cloud[2]: Creation complete after 0s [id=faraz]
aws_iam_user.cloud[5]: Creation complete after 0s [id=steve]
aws_iam_user.cloud[6]: Creation complete after 0s [id=braja]
aws_iam_user.cloud[1]: Creation complete after 0s [id=ken]
aws_iam_user.cloud[4]: Creation complete after 0s [id=peter]
aws_iam_user.cloud[3]: Creation complete after 0s [id=mutsumi]

Apply complete! Resources: 7 added, 0 changed, 0 destroyed.
```

### Exercise 3: Using the Terraform Console for Resource Inspection
**Objective:** Learn to inspect created resources using the console

#### Step 1: Access the console
```bash
terraform console
```

#### Step 2: Find the name of the IAM user at index 6
```hcl
> aws_iam_user.cloud[6].name
"braja"
```

**Alternative method:**
```bash
echo 'aws_iam_user.cloud[6].name' | terraform console
"braja"
```

---

## Part 3: Working with List Variables

### Exercise 4: Using the `index()` function
**Objective:** Find the position of an element in a list

#### Step 1: Examine the list variable
```hcl
variable "sf" {
  type = list
  default = [
    "ryu", "ken", "akuma", "seth", "zangief", "poison", "gen", "oni",
    "thawk", "fang", "rashid", "birdie", "sagat", "bison", "cammy",
    "chun-li", "balrog", "cody", "rolento", "ibuki"
  ]
}
```

#### Step 2: Find the index of "oni"
```hcl
> index(var.sf, "oni")
7
```

**Explanation:** The `index()` function returns the zero-based index of the first occurrence of the given value in the list.

---

## Part 4: Working with Set Variables

### Exercise 5: Understanding Set Types
**Objective:** Work with set variables and understand their properties

#### Step 1: Examine the set variable
```hcl
variable "media" {
  type = set(string)
  default = [ 
    "/media/tails.jpg",
    "/media/eggman.jpg",
    "/media/ultrasonic.jpg",
    "/media/knuckles.jpg",
    "/media/shadow.jpg",
  ]
}
```

**Question:** What type is the variable called `media`?
**Answer:** `set(string)`

#### Step 2: Verify the type in console
```hcl
> type(var.media)
set(string)
```

**Key Differences between List and Set:**
- **List:** Ordered collection that allows duplicates
- **Set:** Unordered collection that doesn't allow duplicates

---

## Part 5: Using `for_each` with Sets

### Exercise 6: Uploading Files to S3
**Objective:** Use `for_each` to upload multiple files to an S3 bucket

#### Step 1: Create the S3 bucket resource
```hcl
resource "aws_s3_bucket" "sonic_media" {
    bucket = var.bucket
}
```

#### Step 2: Create the S3 object upload resource
```hcl
resource "aws_s3_object" "upload_sonic_media" {
  bucket = aws_s3_bucket.sonic_media.id
  for_each = var.media
  source = each.value
  key = basename(each.value)
}
```

**Key Concepts:**
- `for_each = var.media`: Iterates over each element in the set
- `each.value`: The current value in the iteration
- `basename(each.value)`: Extracts the filename from the path (removes `/media/`)

**Explanation of `basename()` function:**
- Input: `/media/eggman.jpg`
- Output: `eggman.jpg`

#### Step 3: Apply the configuration
```bash
terraform apply
```

**Expected Output:**
```
aws_s3_bucket.sonic_media: Creating...
aws_s3_bucket.sonic_media: Creation complete after 1s [id=sonic-media]
aws_s3_object.upload_sonic_media["/media/eggman.jpg"]: Creating...
aws_s3_object.upload_sonic_media["/media/knuckles.jpg"]: Creating...
aws_s3_object.upload_sonic_media["/media/shadow.jpg"]: Creating...
aws_s3_object.upload_sonic_media["/media/tails.jpg"]: Creating...
aws_s3_object.upload_sonic_media["/media/ultrasonic.jpg"]: Creating...
aws_s3_object.upload_sonic_media["/media/knuckles.jpg"]: Creation complete after 0s [id=knuckles.jpg]
aws_s3_object.upload_sonic_media["/media/ultrasonic.jpg"]: Creation complete after 0s [id=ultrasonic.jpg]
aws_s3_object.upload_sonic_media["/media/eggman.jpg"]: Creation complete after 0s [id=eggman.jpg]
aws_s3_object.upload_sonic_media["/media/shadow.jpg"]: Creation complete after 0s [id=shadow.jpg]
aws_s3_object.upload_sonic_media["/media/tails.jpg"]: Creation complete after 0s [id=tails.jpg]

Apply complete! Resources: 6 added, 0 changed, 0 destroyed.
```

---

## Part 6: Conditional Expressions

### Exercise 7: Working with Conditional Logic
**Objective:** Create conditional logic for EC2 instance types

#### Step 1: Navigate to the project directory
```bash
cd /root/terraform-projects/project-mario
```

#### Step 2: Examine the variables
```hcl
variable "small" {
    type = string
    default = "t2.nano"
}

variable "name" {
    type = string
}
```

**Questions:**
1. What is the value of the variable called `small`?
   **Answer:** `"t2.nano"`

2. What is the current value for the variable called `name`?
   **Answer:** `undefined` (no default value provided)

#### Step 3: Create EC2 instance with conditional expression
```hcl
resource "aws_instance" "mario_servers" {
  ami = var.ami
  tags = { Name = var.name }
  instance_type = var.name == "tiny" ? var.small : var.large
}
```

**Conditional Expression Syntax:**
```hcl
condition ? true_value : false_value
```

**Explanation:**
- If `var.name == "tiny"` is true, use `var.small` (t2.nano)
- If `var.name == "tiny"` is false, use `var.large`

#### Step 4: Apply with variable override
```bash
terraform apply -var="name=tiny"
```

**Expected Output:**
```
Plan: 1 to add, 0 to change, 0 destroy.

Do you want to perform these actions?
  Terraform will perform the actions described above.
  Only 'yes' will be accepted to approve.

  Enter a value: yes

aws_instance.mario_servers: Creating...
aws_instance.mario_servers: Still creating... [10s elapsed]
aws_instance.mario_servers: Creation complete after 10s [id=i-98310e35e5ff298ba]

Apply complete! Resources: 1 added, 0 changed, 0 destroyed.
```

---

## Summary of Key Functions and Concepts

### Built-in Functions Used in This Lab:
1. **`floor(number)`** - Returns the largest integer less than or equal to the given number
2. **`title(string)`** - Converts the first letter of each word to uppercase
3. **`split(separator, string)`** - Splits a string into a list based on a separator
4. **`length(list/set)`** - Returns the number of elements in a collection
5. **`index(list, value)`** - Returns the index of a value in a list
6. **`basename(path)`** - Returns the last element of a path
7. **`type(value)`** - Returns the type of a value

### Meta-arguments Used:
1. **`count`** - Creates multiple instances of a resource
2. **`for_each`** - Iterates over a set or map to create resources

### Variable Types Covered:
1. **`string`** - Text values
2. **`list`** - Ordered collection of values
3. **`set(string)`** - Unordered collection of unique string values

### Conditional Expressions:
- **Syntax:** `condition ? true_value : false_value`
- **Use case:** Dynamic resource configuration based on conditions

---

## Best Practices

1. **Use the Terraform Console:** Always test functions and expressions in the console before applying
2. **Variable Types:** Choose appropriate variable types (list vs set) based on your needs
3. **Conditional Logic:** Use conditional expressions for dynamic resource configuration
4. **Function Combinations:** Combine multiple functions for complex data transformations
5. **Documentation:** Comment your code to explain complex function usage

---

## Troubleshooting Tips

1. **Console Testing:** Use `terraform console` to test functions before applying
2. **Type Errors:** Ensure variable types match function expectations
3. **Index Errors:** Remember that list indices start at 0
4. **Path Functions:** Use `basename()` and `dirname()` for file path manipulation
5. **Conditional Logic:** Test both branches of conditional expressions

---

## Next Steps

After completing this lab, you should:
1. Practice using different Terraform functions in your own projects
2. Experiment with conditional expressions for more complex scenarios
3. Explore additional built-in functions in the Terraform documentation
4. Learn about custom functions and modules for advanced use cases

**Reference Documentation:**
- [Terraform Built-in Functions](https://developer.hashicorp.com/terraform/language/functions)
- [Terraform Meta-arguments](https://developer.hashicorp.com/terraform/language/meta-arguments)
- [Terraform Conditional Expressions](https://developer.hashicorp.com/terraform/language/expressions/conditionals)
