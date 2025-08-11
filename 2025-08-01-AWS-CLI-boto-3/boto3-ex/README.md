# AWS VPC Security Architecture Lab Automation

This project automates the complete setup of an AWS VPC Security Architecture Lab using boto3. It creates a secure VPC environment with bastion host, NAT instance, and private instances, following AWS best practices for network security.

## 🏗️ Architecture Overview

The automation creates the following infrastructure:

```
Internet Gateway
       |
   Public Subnet
   |           |
Bastion      NAT Instance
   |           |
   |    Route Table (Private)
   |           |
   +---- Private Subnet ----+
              |
         Private Instance
```

### Components Created:

- **VPC**: Isolated network environment (10.0.0.0/16)
- **Public Subnet**: Internet-accessible subnet for bastion and NAT instances (10.0.1.0/24)
- **Private Subnet**: Secure subnet for backend instances (10.0.2.0/24)
- **Bastion Host**: SSH jump server for secure access to private instances
- **NAT Instance**: Provides outbound internet access for private instances
- **Private Instance**: Backend server with no direct internet access
- **IAM Role**: Enables AWS Systems Manager (SSM) Session Manager connectivity
- **Security Groups**: Properly configured for each component
- **Route Tables**: Configured for public and private traffic routing

## 🚀 Features

- **Complete Automation**: One-command setup of entire VPC infrastructure
- **Security Best Practices**: Proper security groups, private subnets, and access controls
- **Multiple Access Methods**: SSH via bastion host and SSM Session Manager
- **Resource Tagging**: All resources properly tagged for management
- **Error Handling**: Comprehensive error handling and rollback capabilities
- **Cleanup Script**: Easy cleanup of all created resources
- **Colored Output**: User-friendly colored console output
- **Wait Mechanisms**: Proper waiting for resource creation and state changes
- **Comprehensive Logging**: Detailed logging to `app.log` file for debugging and audit trails

## 📋 Prerequisites

1. **AWS Account**: Active AWS account with appropriate permissions
2. **AWS CLI**: Installed and configured with credentials
3. **Python 3.7+**: Python environment with pip
4. **IAM Permissions**: User/role with permissions for:
   - EC2 (full access)
   - IAM (for creating roles and policies)
   - VPC (full access)

## 🛠️ Installation

1. **Clone or download the project files**

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure AWS credentials**:
   ```bash
   aws configure
   ```
   Enter your AWS Access Key ID, Secret Access Key, default region, and output format.

## 🎯 Usage

### Quick Start

Run the complete VPC setup:
```bash
python3 vpc_automation.py
```

### Cleanup

Remove all created resources:
```bash
python3 cleanup.py
```

## 📁 Project Structure

```
boto3-ex/
├── vpc_automation.py      # Main automation script
├── cleanup.py            # Cleanup script
├── test_connection.py    # Connectivity testing script
├── config.py             # Configuration file
├── requirements.txt      # Python dependencies
├── setup.sh              # Setup script
├── README.md            # This file
├── app.log              # Log file (created during execution)
├── key01.pem            # Generated SSH key (after first run)
└── AWS-VPC-Security-Architecture-Lab.md  # Original lab guide
```

## 🔧 Configuration

The automation uses the following default configuration (can be modified in `vpc_automation.py`):

- **Region**: `eu-north-1`
- **VPC CIDR**: `10.0.0.0/16`
- **Public Subnet**: `10.0.1.0/24`
- **Private Subnet**: `10.0.2.0/24`
- **Instance Type**: `t2.micro` (Free Tier eligible)
- **Key Pair Name**: `key01`
- **VPC Name**: `lab-vpc`

## 🔐 Security Features

### Network Security
- **Private Subnet**: Backend instances have no direct internet access
- **Bastion Host**: Single point of SSH access with proper security groups
- **NAT Instance**: Controlled outbound internet access for private instances
- **Security Groups**: Least-privilege access rules

### Access Control
- **SSH Key Management**: Automatic key pair creation and file permissions
- **IAM Roles**: Minimal required permissions for SSM access
- **Session Manager**: Secure web-based access without SSH keys

### Security Groups Configuration
- **Bastion**: SSH (port 22) from anywhere
- **NAT**: All traffic from VPC CIDR
- **Private**: SSH (port 22) from bastion security group only

## 🔗 Connection Methods

### Method 1: SSH via Bastion Host
1. Connect to bastion host:
   ```bash
   ssh -i key01.pem ec2-user@<BASTION_PUBLIC_IP>
   ```

2. Copy private key to bastion:
   ```bash
   scp -i key01.pem key01.pem ec2-user@<BASTION_PUBLIC_IP>:~/
   ```

3. Connect to private instance:
   ```bash
   ssh -i key01.pem ec2-user@<PRIVATE_INSTANCE_IP>
   ```

### Method 2: AWS Systems Manager Session Manager
1. Go to AWS EC2 Console
2. Select the private instance
3. Click "Connect"
4. Choose "Session Manager" tab
5. Click "Connect"

## 📊 Resource Information

After successful setup, the script displays:
- Instance IDs and IP addresses
- SSH connection commands
- Resource tags and states
- Next steps for accessing instances

## 🧹 Cleanup

The cleanup script (`cleanup.py`) removes all resources in the correct order:
1. Terminate EC2 instances
2. Delete security groups
3. Delete subnets
4. Delete route tables
5. Delete internet gateways
6. Delete VPCs
7. Delete key pairs
8. Delete IAM roles and instance profiles

## 📝 Logging

All scripts include comprehensive logging functionality:

- **Log File**: `app.log` - Contains detailed logs of all operations
- **Log Format**: Timestamp, logger name, log level, and message
- **Log Levels**: INFO, WARNING, ERROR, SUCCESS
- **Dual Output**: Both console (colored) and file logging
- **Audit Trail**: Complete record of all AWS operations and their results

### Log File Contents:
- Resource creation/deletion timestamps
- AWS API calls and responses
- Error details and stack traces
- Instance states and IP addresses
- Security group configurations
- Test results and connectivity status

### Viewing Logs:
```bash
# View entire log file
cat app.log

# View recent logs
tail -f app.log

# Search for errors
grep "ERROR" app.log

# Search for specific operations
grep "VPC created" app.log
```

## ⚠️ Important Notes

1. **Cost**: This setup uses Free Tier eligible resources, but monitor your AWS billing
2. **Region**: Default region is `eu-north-1`, change in the script if needed
3. **Key File**: The private key file (`key01.pem`) is created with proper permissions (400)
4. **Cleanup**: Always run cleanup when done to avoid ongoing charges
5. **IAM Permissions**: Ensure your AWS user/role has sufficient permissions

## 🐛 Troubleshooting

### Common Issues

1. **Authentication Errors**:
   ```bash
   aws sts get-caller-identity
   aws configure
   ```

2. **Permission Denied**:
   - Check IAM permissions
   - Ensure user has EC2, VPC, and IAM access

3. **Key File Permissions**:
   ```bash
   chmod 400 key01.pem
   ```

4. **Instance Not Starting**:
   - Check security groups
   - Verify subnet configuration
   - Review CloudWatch logs

### Debug Mode

Enable debug logging in the script:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📚 Learning Resources

- [AWS VPC Documentation](https://docs.aws.amazon.com/vpc/)
- [boto3 Documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)
- [AWS Security Best Practices](https://aws.amazon.com/security/security-learning/)
- [AWS Systems Manager Session Manager](https://docs.aws.amazon.com/systems-manager/latest/userguide/session-manager.html)

## 🤝 Contributing

Feel free to submit issues, feature requests, or pull requests to improve this automation.

## 📄 License

This project is for educational purposes. Use at your own risk and ensure compliance with AWS terms of service.

## ⚡ Quick Commands

```bash
# Setup
pip install -r requirements.txt
aws configure
python3 vpc_automation.py

# Cleanup
python3 cleanup.py

# Check status
aws ec2 describe-instances --filters "Name=tag:Environment,Values=Lab"
```

---

**Happy Learning! 🚀**
