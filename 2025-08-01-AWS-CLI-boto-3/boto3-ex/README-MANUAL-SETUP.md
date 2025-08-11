# Manual Setup Guide - Advanced Users

This guide is for advanced users who prefer manual setup over the automated setup script.

## 🛠️ Manual Installation Steps

### Prerequisites

1. **Python 3.7+**: Installed and available in PATH
2. **pip**: Python package installer
3. **AWS CLI**: Installed and configured
4. **Git**: For cloning the repository

### Step 1: Clone the Repository

```bash
git clone <repository-url>
cd boto3-ex
```

### Step 2: Create Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
# Install required packages
pip install -r requirements.txt
```

### Step 4: Configure AWS Credentials

#### Option A: AWS CLI Configuration

```bash
aws configure
```

Enter your:
- AWS Access Key ID
- AWS Secret Access Key
- Default region (e.g., us-east-1)
- Default output format (json)

#### Option B: Environment Variables

```bash
export AWS_ACCESS_KEY_ID=your_access_key_id
export AWS_SECRET_ACCESS_KEY=your_secret_access_key
export AWS_DEFAULT_REGION=us-east-1
```

#### Option C: Configuration File

Create `~/.aws/credentials`:
```ini
[default]
aws_access_key_id = your_access_key_id
aws_secret_access_key = your_secret_access_key
```

Create `~/.aws/config`:
```ini
[default]
region = us-east-1
output = json
```

### Step 5: Verify Installation

```bash
# Test AWS credentials
aws sts get-caller-identity

# Test Python packages
python3 -c "import boto3; print('boto3 version:', boto3.__version__)"
```

## 🎯 Usage

After manual setup, you can use the same commands:

```bash
# Activate virtual environment (if not already active)
source venv/bin/activate

# Run VPC automation
python3 vpc_automation.py

# Test connectivity
python3 test_connection.py

# Clean up resources
python3 cleanup.py
```

## 🔧 Troubleshooting

### Virtual Environment Issues

```bash
# If virtual environment creation fails
python3 -m venv --help

# If pip install fails
pip install --upgrade pip
```

### AWS Credentials Issues

```bash
# Test AWS CLI
aws --version

# Test credentials
aws sts get-caller-identity

# List configured profiles
aws configure list-profiles
```

### Python Package Issues

```bash
# Check installed packages
pip list

# Reinstall packages
pip install --force-reinstall -r requirements.txt
```

## 📚 Additional Resources

- [Python Virtual Environments](https://docs.python.org/3/tutorial/venv.html)
- [AWS CLI Configuration](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-files.html)
- [boto3 Documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)

---

**Note**: For most users, the automated setup script (`./setup.sh`) is recommended as it handles all these steps automatically and provides better error handling and user guidance.
