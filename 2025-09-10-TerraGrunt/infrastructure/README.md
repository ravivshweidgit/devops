# Terragrunt Infrastructure Project

This project demonstrates how to build a complete AWS infrastructure using **Terraform** and **Terragrunt** with multiple environments (dev, staging, prod).

## 🎯 What We Built

A complete AWS infrastructure with:
- **VPC** with public and private subnets
- **RDS MySQL** database in private subnets
- **EC2 Bastion Host** for secure database access
- **Multi-environment** setup (dev, staging)
- **Infrastructure as Code** best practices

## 📁 Project Structure

```
infrastructure/
├── modules/                    # Reusable Terraform modules
│   ├── vpc/                   # VPC module
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── output.tf
│   ├── rds/                   # RDS module
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── output.tf
│   └── ec2/                   # EC2 module
│       ├── main.tf
│       ├── variables.tf
│       └── output.tf
├── terragrunt/                # Terragrunt configurations
│   └── aws/
│       ├── terragrunt.hcl     # Root configuration
│       ├── vpc/
│       │   ├── dev/
│       │   │   └── terragrunt.hcl
│       │   └── staging/
│       │       └── terragrunt.hcl
│       ├── rds/
│       │   ├── dev/
│       │   │   └── terragrunt.hcl
│       │   └── staging/
│       │       └── terragrunt.hcl
│       └── ec2/
│           └── dev/
│               └── terragrunt.hcl
└── bootstrap/                 # Bootstrap configuration
    ├── main.tf
    └── outputs.tf
```

## 🚀 Getting Started

### Prerequisites

1. **AWS CLI** configured with credentials
2. **Terraform** installed
3. **Terragrunt** installed
4. **SSH key pair** for EC2 access

### Initial Setup

1. **Clone the repository**
   ```bash
   git clone <your-repo>
   cd infrastructure
   ```

2. **Configure AWS credentials**
   ```bash
   aws configure
   ```

3. **Generate SSH key for bastion host**
   ```bash
   ssh-keygen -t rsa -b 2048 -f ~/.ssh/bastion-key -N ""
   ```

## 🏗️ Infrastructure Components

### 1. VPC Module (`modules/vpc/`)

Creates a complete VPC with:
- **VPC**: Main virtual private cloud
- **Public Subnets**: For bastion hosts (10.0.10.0/24, 10.0.11.0/24)
- **Private Subnets**: For databases (10.0.1.0/24, 10.0.2.0/24)
- **Internet Gateway**: For public subnet internet access
- **Route Tables**: Proper routing configuration
- **Security Groups**: Database access control
- **DB Subnet Group**: For RDS deployment

### 2. RDS Module (`modules/rds/`)

Creates MySQL database with:
- **MySQL 8.0.42**: Latest supported version
- **db.t3.micro**: Free tier eligible instance
- **20GB Storage**: Free tier eligible
- **Private Subnets**: Secure deployment
- **Security Groups**: Controlled access

### 3. EC2 Module (`modules/ec2/`)

Creates bastion host with:
- **Amazon Linux 2**: Latest AMI
- **t2.micro**: Free tier eligible
- **MySQL Client**: Pre-installed
- **SSH Access**: Key-based authentication
- **Public Subnet**: Internet accessible

## 🌍 Multi-Environment Setup

### Development Environment
- **VPC ID**: `vpc-001395dda43964164`
- **RDS Endpoint**: `raviv-project-dev-db.cs54ki4k01sz.us-east-1.rds.amazonaws.com:3306`
- **Database**: `myappdb_dev`
- **Bastion IP**: `44.204.128.67`

### Staging Environment
- **VPC ID**: `vpc-0ef1279da3374bbd4`
- **RDS Endpoint**: `raviv-project-staging-db.cs54ki4k01sz.us-east-1.rds.amazonaws.com:3306`
- **Database**: `myappdb_staging`

## 📋 Deployment Commands

### Deploy Development Environment

1. **Deploy VPC**
   ```bash
   cd terragrunt/aws/vpc/dev
   terragrunt apply
   ```

2. **Deploy RDS**
   ```bash
   cd terragrunt/aws/rds/dev
   terragrunt apply
   ```

3. **Deploy Bastion Host**
   ```bash
   cd terragrunt/aws/ec2/dev
   terragrunt apply
   ```

### Deploy Staging Environment

1. **Deploy VPC**
   ```bash
   cd terragrunt/aws/vpc/staging
   terragrunt apply
   ```

2. **Deploy RDS**
   ```bash
   cd terragrunt/aws/rds/staging
   terragrunt apply
   ```

## 💻 Complete CLI Session Documentation

### Initial Setup and Troubleshooting

1. **First Terragrunt Init Attempt (Failed)**
   ```bash
   cd terragrunt/aws/vpc/dev
   terragrunt init
   ```
   **Error**: `S3 bucket "ravivsh-us-east-kuku-riku" does not exist`

2. **Fixed Backend Configuration and Retried**
   ```bash
   terragrunt init
   ```
   **Result**: ✅ Successfully initialized with local backend

3. **First Terragrunt Apply (VPC)**
   ```bash
   terragrunt apply
   ```
   **Result**: Created VPC, private subnets, security groups, and DB subnet group

### Discovering Infrastructure Details

4. **Getting VPC Outputs**
   ```bash
   terragrunt output
   ```
   **Output**:
   ```
   db_subnet_group_name = "raviv-project-dev-rds"
   private_subnet_ids = [
     "subnet-08d2217acc92f1e62",
     "subnet-0e3fdefb3a813da1e",
   ]
   security_group_id = "sg-0bcd7ef210da8dc0a"
   vpc_id = "vpc-001395dda43964164"
   ```

5. **Deploying RDS Database**
   ```bash
   cd ../rds/dev
   terragrunt apply
   ```
   **Result**: Created MySQL RDS instance

6. **Getting RDS Outputs (Initial - Failed)**
   ```bash
   terragrunt output
   ```
   **Error**: `No outputs found` - because outputs weren't defined yet

7. **Adding RDS Outputs and Reapplying**
   ```bash
   terragrunt apply -auto-approve
   ```
   **Result**: Added comprehensive outputs

8. **Getting RDS Connection Details**
   ```bash
   terragrunt output
   ```
   **Output**:
   ```
   rds_database_name = "myappdb_dev"
   rds_endpoint = "raviv-project-dev-db.cs54ki4k01sz.us-east-1.rds.amazonaws.com:3306"
   rds_identifier = "raviv-project-dev-db"
   rds_port = 3306
   rds_username = <sensitive>
   ```

9. **Getting Specific RDS Endpoint**
   ```bash
   terragrunt output rds_endpoint
   ```
   **Output**: `"raviv-project-dev-db.cs54ki4k01sz.us-east-1.rds.amazonaws.com:3306"`

### Adding Public Subnets and Bastion Host

10. **Updating VPC with Public Subnets**
    ```bash
    cd ../../vpc/dev
    terragrunt apply -auto-approve
    ```
    **Result**: Added public subnets, internet gateway, and route tables

11. **Getting Updated VPC Outputs**
    ```bash
    terragrunt output
    ```
    **Output**:
    ```
    db_subnet_group_name = "raviv-project-dev-rds"
    private_subnet_ids = [
      "subnet-08d2217acc92f1e62",
      "subnet-0e3fdefb3a813da1e",
    ]
    public_subnet_ids = [
      "subnet-0b10ef55c85dff106",
      "subnet-0121d6c78864102c9",
    ]
    security_group_id = "sg-0bcd7ef210da8dc0a"
    vpc_id = "vpc-001395dda43964164"
    ```

12. **Generating SSH Key for Bastion**
    ```bash
    ssh-keygen -t rsa -b 2048 -f ~/.ssh/bastion-key -N "" -C "bastion-key"
    ```
    **Result**: Created SSH key pair for bastion host access

13. **Getting Public Key for Configuration**
    ```bash
    cat ~/.ssh/bastion-key.pub
    ```
    **Output**: `ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCI2iUIZubvCZgs59KSOKjNXEMVEEFJQhh3k9tJ29Qu/lApjq9ptJ2sGeSbjLi1z5sqvh/D1SFS7a0HeBeRqdH9msfTZ8BBZMQBj15qZCaNA2FMfWxLxW6LW4JI3U6bx/thr4HESufdO/KCsLDMi28mlgnc2xkPxrCnhQHRVN3eq+sX7YhQrbct6lxl293NIot1ttpT6p6yhqT2OzFrdw8duG9fpcmTn09ftATezehDjMsiNF7GsmJ4enex9XLXwJPiOlOGt9pk9VsHJgDKeVn0KjdEjaVrVA8Ihw3dA4gQjWerPkH53YQYEVjmM49wKdrg1dA2uBhQHnBysSn9V+dZ bastion-key`

14. **Deploying Bastion Host**
    ```bash
    cd ../../ec2/dev
    terragrunt apply -auto-approve
    ```
    **Result**: Created EC2 bastion host with MySQL client

15. **Getting Bastion Host Details**
    ```bash
    terragrunt output
    ```
    **Output**:
    ```
    bastion_private_ip = "10.0.10.5"
    bastion_public_ip = "44.204.128.67"
    bastion_security_group_id = "sg-05102f8c7e0388ce8"
    key_name = "raviv-project-dev-bastion-key"
    ```

### Testing Database Connection

16. **Testing RDS Connection via Bastion**
    ```bash
    ssh -i ~/.ssh/bastion-key -o StrictHostKeyChecking=no ec2-user@44.204.128.67 "mysql -h raviv-project-dev-db.cs54ki4k01sz.us-east-1.rds.amazonaws.com -u admin -p'your-secure-password' myappdb_dev -e 'SELECT VERSION();'"
    ```
    **Result**: ✅ Successfully connected and returned `VERSION() 8.0.42`

### Staging Environment Deployment

17. **Checking Staging VPC Status**
    ```bash
    cd ../../vpc/staging
    terragrunt output
    ```
    **Output**:
    ```
    db_subnet_group_name = "raviv-project-staging-rds"
    private_subnet_ids = [
      "subnet-04be4257fae57b4ea",
      "subnet-0aaa0fb83343fdadc",
    ]
    public_subnet_ids = [
      "subnet-05e0b929f4578e195",
      "subnet-0da99df10e26c8fd0",
    ]
    security_group_id = "sg-0590d60e2986f4ed8"
    vpc_id = "vpc-0ef1279da3374bbd4"
    ```

18. **Deploying Staging RDS**
    ```bash
    cd ../../rds/staging
    terragrunt apply
    ```
    **Result**: Created staging MySQL RDS instance

19. **Getting Staging RDS Details**
    ```bash
    terragrunt output
    ```
    **Output**:
    ```
    rds_database_name = "myappdb_staging"
    rds_endpoint = "raviv-project-staging-db.cs54ki4k01sz.us-east-1.rds.amazonaws.com:3306"
    rds_identifier = "raviv-project-staging-db"
    rds_port = 3306
    rds_username = <sensitive>
    ```

### Key Discovery Commands

20. **Finding RDS Endpoints**
    ```bash
    # Development RDS endpoint
    cd ../../rds/dev
    terragrunt output rds_endpoint
    # Output: "raviv-project-dev-db.cs54ki4k01sz.us-east-1.rds.amazonaws.com:3306"
    
    # Staging RDS endpoint
    cd ../staging
    terragrunt output rds_endpoint
    # Output: "raviv-project-staging-db.cs54ki4k01sz.us-east-1.rds.amazonaws.com:3306"
    ```

21. **Finding Bastion Host IP**
    ```bash
    cd ../../ec2/dev
    terragrunt output bastion_public_ip
    # Output: "44.204.128.67"
    ```

22. **Finding VPC IDs**
    ```bash
    # Development VPC
    cd ../../vpc/dev
    terragrunt output vpc_id
    # Output: "vpc-001395dda43964164"
    
    # Staging VPC
    cd ../staging
    terragrunt output vpc_id
    # Output: "vpc-0ef1279da3374bbd4"
    ```

### Useful Output Commands Summary

```bash
# Get all outputs for a module
terragrunt output

# Get specific output
terragrunt output <output_name>

# Common outputs to check:
terragrunt output vpc_id
terragrunt output rds_endpoint
terragrunt output bastion_public_ip
terragrunt output security_group_id
terragrunt output public_subnet_ids
terragrunt output private_subnet_ids
```

## 🔐 Database Connection

### Connect via Bastion Host

1. **SSH to bastion**
   ```bash
   ssh -i ~/.ssh/bastion-key ec2-user@44.204.128.67
   ```

2. **Connect to database**
   ```bash
   mysql -h raviv-project-dev-db.cs54ki4k01sz.us-east-1.rds.amazonaws.com \
         -u admin -p myappdb_dev
   ```

3. **One-liner connection**
   ```bash
   ssh -i ~/.ssh/bastion-key ec2-user@44.204.128.67 \
       "mysql -h raviv-project-dev-db.cs54ki4k01sz.us-east-1.rds.amazonaws.com \
        -u admin -p'your-secure-password' myappdb_dev"
   ```

### SSH Tunnel for GUI Tools

```bash
ssh -i ~/.ssh/bastion-key -L 3306:raviv-project-dev-db.cs54ki4k01sz.us-east-1.rds.amazonaws.com:3306 ec2-user@44.204.128.67
```

Then connect to `localhost:3306` in your MySQL GUI tool.

## 🔧 Key Concepts Learned

### 1. Terragrunt vs Terraform
- **Terraform**: Infrastructure provisioning tool
- **Terragrunt**: Wrapper that adds DRY principles and environment management

### 2. Module Structure
- **Modules**: Reusable Terraform configurations
- **Variables**: Input parameters for modules
- **Outputs**: Values returned by modules

### 3. Dependencies
- **Dependency blocks**: Ensure proper deployment order
- **Output references**: Share data between modules

### 4. Backend Configuration
- **Local backend**: For development (current setup)
- **S3 backend**: For production (bootstrap configuration provided)

### 5. Security Best Practices
- **Private subnets**: For sensitive resources (databases)
- **Public subnets**: For internet-facing resources (bastion hosts)
- **Security groups**: Network-level access control
- **Bastion hosts**: Secure access to private resources

## 🚨 Common Issues & Solutions

### Issue 1: S3 Backend Bucket Doesn't Exist
**Error**: `S3 bucket "bucket-name" does not exist`

**Solution**: Use the bootstrap configuration to create the bucket first:
```bash
cd bootstrap
terraform init
terraform apply
```

### Issue 2: Missing Backend Configuration
**Error**: `Found remote_state settings but no backend block`

**Solution**: Add backend block to modules:
```hcl
terraform {
  backend "local" {}
}
```

### Issue 3: Missing Dependencies
**Error**: `dependency.vpc.outputs.security_group_id` not found

**Solution**: Add dependency block:
```hcl
dependency "vpc" {
  config_path = "../../vpc/dev"
}
```

## 🔧 Code Changes & Fixes Made During Development

### Fix 1: Backend Configuration in Modules

**Problem**: Modules had `backend "s3" {}` but S3 bucket didn't exist, causing initialization failures.

**Original Code** (`modules/vpc/main.tf` and `modules/rds/main.tf`):
```hcl
terraform {
  backend "s3" {}
}
```

**Fixed Code**:
```hcl
terraform {
  backend "local" {}
}
```

**Why**: In Terragrunt setups, backend configuration is managed by Terragrunt, but Terraform still needs to declare a backend block.

### Fix 2: Missing Variables in RDS Configuration

**Problem**: RDS module expected `project` and `aws_region` variables but they weren't being passed.

**Original Code** (`terragrunt/aws/rds/dev/terragrunt.hcl`):
```hcl
inputs = {
  environment          = "dev"
  db_name              = "myappdb_dev"
  db_username          = "admin"
  db_password          = "your-secure-password"
  vpc_security_group_ids = [dependency.vpc.outputs.security_group_id]
  db_subnet_group_name  = dependency.vpc.outputs.db_subnet_group_name
}
```

**Fixed Code**:
```hcl
inputs = {
  environment          = "dev"
  project              = "raviv-project"  # Added
  aws_region           = "us-east-1"      # Added
  db_name              = "myappdb_dev"
  db_username          = "admin"
  db_password          = "your-secure-password"
  vpc_security_group_ids = [dependency.vpc.outputs.security_group_id]
  db_subnet_group_name  = dependency.vpc.outputs.db_subnet_group_name
}
```

**Why**: The RDS module's `variables.tf` required these variables, but they weren't being provided.

### Fix 3: Using Root Terragrunt Configuration

**Problem**: Duplicating common variables across environments.

**Solution**: Use `include "root"` to inherit common variables from root `terragrunt.hcl`:

**Root Configuration** (`terragrunt/aws/terragrunt.hcl`):
```hcl
inputs = {
  aws_region = "us-east-1"
  project    = "raviv-project"
}
```

**Local Configuration** (`terragrunt/aws/rds/dev/terragrunt.hcl`):
```hcl
include "root" {
  path = find_in_parent_folders()
}

inputs = {
  environment          = "dev"
  # project and aws_region inherited from root
  db_name              = "myappdb_dev"
  db_username          = "admin"
  db_password          = "your-secure-password"
  vpc_security_group_ids = [dependency.vpc.outputs.security_group_id]
  db_subnet_group_name  = dependency.vpc.outputs.db_subnet_group_name
}
```

### Fix 4: Adding Public Subnets to VPC

**Problem**: VPC only had private subnets, needed public subnets for bastion host.

**Added to** `modules/vpc/main.tf`:
```hcl
# Public subnets
resource "aws_subnet" "public" {
  count                   = 2
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.${count.index + 10}.0/24"
  availability_zone       = data.aws_availability_zones.available.names[count.index]
  map_public_ip_on_launch = true

  tags = {
    Name        = "${var.project}-${var.environment}-public-${count.index + 1}"
    Environment = var.environment
    Project     = var.project
  }
}

# Internet Gateway
resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name        = "${var.project}-${var.environment}-igw"
    Environment = var.environment
    Project     = var.project
  }
}

# Route table for public subnets
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id
  }

  tags = {
    Name        = "${var.project}-${var.environment}-public-rt"
    Environment = var.environment
    Project     = var.project
  }
}

# Route table associations for public subnets
resource "aws_route_table_association" "public" {
  count          = 2
  subnet_id      = aws_subnet.public[count.index].id
  route_table_id = aws_route_table.public.id
}
```

**Updated** `modules/vpc/output.tf`:
```hcl
output "public_subnet_ids" {
  value = aws_subnet.public[*].id
}
```

### Fix 5: Missing Dependency Block in Staging RDS

**Problem**: Staging RDS configuration was missing the dependency block.

**Original Code** (`terragrunt/aws/rds/staging/terragrunt.hcl`):
```hcl
include "root" {
  path = find_in_parent_folders()
}

terraform {
  source = "../../../../modules/rds"
}

inputs = {
  environment  = "staging"
  db_name      = "myappdb_staging"
  db_username  = "admin"
  db_password  = "your-secure-password"
  vpc_security_group_ids = [dependency.vpc.outputs.security_group_id]
  db_subnet_group_name  = dependency.vpc.outputs.db_subnet_group_name
}
```

**Fixed Code**:
```hcl
include "root" {
  path = find_in_parent_folders()
}

dependency "vpc" {  # Added this block
  config_path = "../../vpc/staging"
}

terraform {
  source = "../../../../modules/rds"
}

inputs = {
  environment  = "staging"
  db_name      = "myappdb_staging"
  db_username  = "admin"
  db_password  = "your-secure-password"
  vpc_security_group_ids = [dependency.vpc.outputs.security_group_id]
  db_subnet_group_name  = dependency.vpc.outputs.db_subnet_group_name
}
```

### Fix 6: Backend Configuration Strategy

**Problem**: S3 backend bucket didn't exist, causing initialization failures.

**Solution**: Switched to local backend for development:

**Updated** `terragrunt/aws/terragrunt.hcl`:
```hcl
# Option 1: Use local backend initially (comment out remote_state block)
# remote_state {
#   backend = "s3"
#   config = {
#     bucket         = "ravivsh-us-east-kuku-riku"
#     key            = "${path_relative_to_include()}/terraform.tfstate"
#     region         = "us-east-1"
#     encrypt        = true
#     dynamodb_table = "terraform-locks"
#   }
# }

# Option 2: Use local backend for now
remote_state {
  backend = "local"
  config = {
    path = "${path_relative_to_include()}/terraform.tfstate"
  }
}
```

### Fix 7: RDS Output Configuration

**Problem**: RDS module had minimal outputs, needed more connection information.

**Original Code** (`modules/rds/output.tf`):
```hcl
output "rds_endpoint" {
  value = aws_db_instance.rds_instance.endpoint
}
```

**Enhanced Code**:
```hcl
output "rds_endpoint" {
  description = "RDS instance endpoint"
  value       = aws_db_instance.rds_instance.endpoint
}

output "rds_port" {
  description = "RDS instance port"
  value       = aws_db_instance.rds_instance.port
}

output "rds_identifier" {
  description = "RDS instance identifier"
  value       = aws_db_instance.rds_instance.identifier
}

output "rds_username" {
  description = "RDS instance username"
  value       = aws_db_instance.rds_instance.username
  sensitive   = true
}

output "rds_database_name" {
  description = "RDS database name"
  value       = aws_db_instance.rds_instance.db_name
}
```

## 📝 Development Process Summary

1. **Started with S3 backend issues** → Switched to local backend
2. **Fixed module backend configurations** → Added proper backend blocks
3. **Resolved missing variables** → Added project and aws_region
4. **Implemented DRY principles** → Used root terragrunt configuration
5. **Added public subnets** → Enabled bastion host deployment
6. **Created EC2 module** → Built bastion host for database access
7. **Fixed staging dependencies** → Added proper dependency blocks
8. **Enhanced outputs** → Provided complete connection information

## 🎯 Key Lessons Learned

- **Terragrunt manages backends**, but Terraform still needs backend blocks
- **Dependencies are crucial** for proper deployment order
- **Root configurations** eliminate duplication
- **Public subnets** are needed for internet-facing resources
- **Bastion hosts** provide secure access to private resources
- **Outputs** should provide all necessary connection information

## 📊 Infrastructure Diagram

```
Internet → Bastion Host (Public Subnet) → VPC
                                    ├── Public Subnets (10.0.10.0/24, 10.0.11.0/24)
                                    └── Private Subnets (10.0.1.0/24, 10.0.2.0/24)
                                        └── RDS MySQL Database
```

## 🎓 Learning Outcomes

After completing this project, you should understand:

1. **Infrastructure as Code**: How to define infrastructure in code
2. **Terragrunt**: DRY principles and environment management
3. **AWS Networking**: VPCs, subnets, security groups, route tables
4. **Database Security**: Private subnets, bastion hosts, security groups
5. **Multi-Environment**: Separate dev/staging/prod environments
6. **Dependencies**: How modules depend on each other
7. **Best Practices**: Security, organization, and maintainability

## 🗑️ Destroying Resources (Cleanup)

**Important**: Always destroy resources when you're done to avoid AWS charges!

### Destroy in Reverse Order (Dependencies First)

1. **Destroy Bastion Host (EC2)**
   ```bash
   cd terragrunt/aws/ec2/dev
   terragrunt destroy
   ```

2. **Destroy RDS Instances**
   ```bash
   # Destroy staging RDS
   cd ../../rds/staging
   terragrunt destroy
   
   # Destroy dev RDS
   cd ../dev
   terragrunt destroy
   ```

3. **Destroy VPCs (Last)**
   ```bash
   # Destroy staging VPC
   cd ../../vpc/staging
   terragrunt destroy
   
   # Destroy dev VPC
   cd ../dev
   terragrunt destroy
   ```

### Complete Cleanup Commands

```bash
# Navigate to infrastructure directory
cd /path/to/infrastructure

# Destroy all resources in correct order
cd terragrunt/aws/ec2/dev && terragrunt destroy -auto-approve
cd ../../rds/staging && terragrunt destroy -auto-approve
cd ../dev && terragrunt destroy -auto-approve
cd ../../vpc/staging && terragrunt destroy -auto-approve
cd ../dev && terragrunt destroy -auto-approve
```

### Verify Cleanup

```bash
# Check AWS console or use AWS CLI
aws ec2 describe-instances --query 'Reservations[*].Instances[*].[InstanceId,State.Name]' --output table
aws rds describe-db-instances --query 'DBInstances[*].[DBInstanceIdentifier,DBInstanceStatus]' --output table
aws ec2 describe-vpcs --query 'Vpcs[*].[VpcId,State]' --output table
```

### Clean Up Local Files

```bash
# Remove Terragrunt cache directories
find . -name ".terragrunt-cache" -type d -exec rm -rf {} +

# Remove Terraform state files
find . -name "terraform.tfstate*" -delete

# Remove SSH keys (optional)
rm -f ~/.ssh/bastion-key*
```

## 🔄 Next Steps

1. **Add Production Environment**: Create prod configurations
2. **Implement S3 Backend**: Use remote state storage
3. **Add Monitoring**: CloudWatch logs and metrics
4. **Set up CI/CD**: Automated deployments
5. **Add More Resources**: Load balancers, auto-scaling groups
6. **Implement Secrets Management**: AWS Secrets Manager for passwords

## 📚 Additional Resources

- [Terragrunt Documentation](https://terragrunt.gruntwork.io/)
- [Terraform AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/latest)
- [AWS VPC User Guide](https://docs.aws.amazon.com/vpc/)
- [AWS RDS User Guide](https://docs.aws.amazon.com/rds/)

## 🤝 Contributing

This is a learning project. Feel free to:
- Add more environments
- Implement additional modules
- Improve security configurations
- Add monitoring and logging

---

**Happy Learning! 🚀**

*This project demonstrates real-world infrastructure patterns used in production environments.*
