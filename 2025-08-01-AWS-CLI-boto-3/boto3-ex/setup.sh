#!/bin/bash

# AWS VPC Security Architecture Lab Automation - Setup Script
# This script helps set up the environment for the VPC automation project

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    local message="$1"
    local status="$2"
    
    case $status in
        "SUCCESS")
            echo -e "${GREEN}✅ $message${NC}"
            ;;
        "ERROR")
            echo -e "${RED}❌ $message${NC}"
            ;;
        "WARNING")
            echo -e "${YELLOW}⚠️  $message${NC}"
            ;;
        "INFO")
            echo -e "${BLUE}ℹ️  $message${NC}"
            ;;
        "HEADER")
            echo -e "${CYAN}$message${NC}"
            ;;
    esac
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check Python version
check_python_version() {
    if command_exists python3; then
        python_version=$(python3 --version 2>&1 | awk '{print $2}')
        print_status "Found Python $python_version" "SUCCESS"
        
        # Check if version is 3.7 or higher
        if python3 -c "import sys; exit(0 if sys.version_info >= (3, 7) else 1)"; then
            print_status "Python version is compatible (3.7+)" "SUCCESS"
            return 0
        else
            print_status "Python version $python_version is too old. Please install Python 3.7 or higher." "ERROR"
            return 1
        fi
    else
        print_status "Python 3 not found. Please install Python 3.7 or higher." "ERROR"
        return 1
    fi
}

# Function to install AWS CLI
install_aws_cli() {
    print_status "Installing AWS CLI v2..." "INFO"
    
    # Check if we have curl and unzip
    if ! command_exists curl; then
        print_status "curl not found. Please install curl first." "ERROR"
        return 1
    fi
    
    if ! command_exists unzip; then
        print_status "unzip not found. Please install unzip first." "ERROR"
        return 1
    fi
    
    # Create temporary directory
    local temp_dir=$(mktemp -d)
    cd "$temp_dir"
    
    # Download AWS CLI
    print_status "Downloading AWS CLI v2..." "INFO"
    if curl -s "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"; then
        print_status "Download completed" "SUCCESS"
    else
        print_status "Failed to download AWS CLI" "ERROR"
        cd - > /dev/null
        rm -rf "$temp_dir"
        return 1
    fi
    
    # Extract and install
    print_status "Extracting and installing AWS CLI..." "INFO"
    if unzip -q awscliv2.zip && sudo ./aws/install --update; then
        print_status "AWS CLI v2 installed successfully" "SUCCESS"
        cd - > /dev/null
        rm -rf "$temp_dir"
        return 0
    else
        print_status "Failed to install AWS CLI" "ERROR"
        cd - > /dev/null
        rm -rf "$temp_dir"
        return 1
    fi
}

# Function to check AWS CLI
check_aws_cli() {
    local check_only="$1"
    
    if command_exists aws; then
        aws_version=$(aws --version 2>&1 | awk '{print $1}')
        print_status "Found $aws_version" "SUCCESS"
        return 0
    else
        print_status "AWS CLI not found." "ERROR"
        
        if [ "$check_only" != "--check-only" ]; then
            echo ""
            print_status "Would you like to install AWS CLI v2 automatically? (y/n)" "INFO"
            read -r response
            if [[ "$response" =~ ^[Yy]$ ]]; then
                if install_aws_cli; then
                    # Verify installation
                    if command_exists aws; then
                        aws_version=$(aws --version 2>&1 | awk '{print $1}')
                        print_status "AWS CLI installation verified: $aws_version" "SUCCESS"
                        return 0
                    else
                        print_status "AWS CLI installation failed verification" "ERROR"
                        return 1
                    fi
                else
                    print_status "AWS CLI installation failed" "ERROR"
                    return 1
                fi
            else
                print_status "'./setup.sh' will install AWS CLI automatically when not in check-only mode" "INFO"
                return 1
            fi
        else
            print_status "'./setup.sh' will install AWS CLI automatically when not in check-only mode" "INFO"
            return 1
        fi
    fi
}

# Function to read AWS credentials from config file
read_aws_config() {
    if [ -f "aws.cfg" ]; then
        print_status "Found aws.cfg file, reading credentials..." "INFO"
        
        # Read values from aws.cfg using grep and cut
        local access_key=$(grep "^access_key_id" aws.cfg | cut -d'=' -f2 | tr -d ' ')
        local secret_key=$(grep "^secret_access_key" aws.cfg | cut -d'=' -f2 | tr -d ' ')
        local region=$(grep "^region" aws.cfg | cut -d'=' -f2 | tr -d ' ')
        local output_format=$(grep "^output_format" aws.cfg | cut -d'=' -f2 | tr -d ' ')
        
        # Set defaults if not found
        region=${region:-us-east-1}
        output_format=${output_format:-json}
        
        # Check for placeholder values and guide user
        local needs_update=false
        
        if [ "$access_key" = "YOUR_ACCESS_KEY_ID_HERE" ] || [ -z "$access_key" ]; then
            print_status "Please update 'access_key_id' in aws.cfg file with your AWS Access Key ID" "ERROR"
            needs_update=true
        fi
        
        if [ "$secret_key" = "YOUR_SECRET_ACCESS_KEY_HERE" ] || [ -z "$secret_key" ]; then
            print_status "Please update 'secret_access_key' in aws.cfg file with your AWS Secret Access Key" "ERROR"
            needs_update=true
        fi
        
        if [ "$region" = "YOUR_REGION_HERE" ] || [ -z "$region" ]; then
            print_status "Please update 'region' in aws.cfg file with your AWS region (e.g., us-east-1)" "ERROR"
            needs_update=true
        fi
        
        if [ "$needs_update" = true ]; then
            print_status "After updating aws.cfg, run './setup.sh' again" "INFO"
            return 1
        fi
        
        # Check if credentials are valid
        if [ -n "$access_key" ] && [ -n "$secret_key" ] && [ -n "$region" ]; then
            print_status "AWS credentials found in aws.cfg file" "SUCCESS"
            
            # Configure AWS CLI with file credentials
            if aws configure set aws_access_key_id "$access_key" && \
               aws configure set aws_secret_access_key "$secret_key" && \
               aws configure set default.region "$region" && \
               aws configure set default.output "$output_format"; then
                print_status "AWS credentials configured from aws.cfg file" "SUCCESS"
                return 0
            else
                print_status "Failed to configure AWS credentials from aws.cfg file" "ERROR"
                return 1
            fi
        else
            print_status "aws.cfg file found but credentials are not properly configured" "WARNING"
            return 1
        fi
    fi
    return 1
}

# Function to configure AWS credentials
configure_aws_credentials() {
    print_status "Configuring AWS credentials..." "INFO"
    echo ""
    
    # First try to read from aws.cfg file
    if read_aws_config; then
        return 0
    fi
    
    print_status "Please enter your AWS credentials:" "INFO"
    echo ""
    
    # Prompt for AWS credentials
    read -p "AWS Access Key ID: " aws_access_key
    read -s -p "AWS Secret Access Key: " aws_secret_key
    echo ""
    read -p "Default region (e.g., us-east-1): " aws_region
    read -p "Default output format (json): " aws_output_format
    
    # Set default values if empty
    aws_region=${aws_region:-us-east-1}
    aws_output_format=${aws_output_format:-json}
    
    # Configure AWS CLI
    if aws configure set aws_access_key_id "$aws_access_key" && \
       aws configure set aws_secret_access_key "$aws_secret_key" && \
       aws configure set default.region "$aws_region" && \
       aws configure set default.output "$aws_output_format"; then
        print_status "AWS credentials configured successfully" "SUCCESS"
        return 0
    else
        print_status "Failed to configure AWS credentials" "ERROR"
        return 1
    fi
}

# Function to check AWS credentials
check_aws_credentials() {
    local check_only="$1"
    
    # First check if credentials are already configured
    if aws sts get-caller-identity >/dev/null 2>&1; then
        identity=$(aws sts get-caller-identity --query 'Arn' --output text)
        print_status "AWS credentials configured: $identity" "SUCCESS"
        return 0
    fi
    
    # Check if environment variables are set
    if [ -n "$AWS_ACCESS_KEY_ID" ] && [ -n "$AWS_SECRET_ACCESS_KEY" ]; then
        print_status "AWS credentials found in environment variables" "SUCCESS"
        return 0
    fi
    
    # If not configured and not in check-only mode, offer to configure
    if [ "$check_only" != "--check-only" ]; then
        print_status "AWS credentials not configured." "ERROR"
        echo ""
        print_status "Would you like to configure AWS credentials now? (y/n)" "INFO"
        read -r response
        if [[ "$response" =~ ^[Yy]$ ]]; then
            if configure_aws_credentials; then
                # Verify configuration
                if aws sts get-caller-identity >/dev/null 2>&1; then
                    identity=$(aws sts get-caller-identity --query 'Arn' --output text)
                    print_status "AWS credentials verified: $identity" "SUCCESS"
                    return 0
                else
                    print_status "AWS credentials verification failed" "ERROR"
                    return 1
                fi
            else
                print_status "AWS credentials configuration failed" "ERROR"
                return 1
            fi
        else
            print_status "AWS credentials configuration skipped" "WARNING"
            print_status "You can configure credentials later with 'aws configure'" "INFO"
            return 1
        fi
    else
        print_status "AWS credentials not configured or invalid." "ERROR"
        print_status "'./setup.sh' will configure AWS credentials automatically when not in check-only mode" "INFO"
        return 1
    fi
}

# Function to check virtual environment
check_virtual_env() {
    if [ -d "venv" ] && [ -f "venv/bin/activate" ]; then
        print_status "Virtual environment found: venv/" "SUCCESS"
        return 0
    else
        print_status "Virtual environment not found." "ERROR"
        print_status "'./setup.sh' will create virtual environment automatically when not in check-only mode" "INFO"
        return 1
    fi
}

# Function to check dependencies
check_dependencies() {
    if [ -d "venv" ]; then
        # Activate virtual environment and check if key packages are installed
        source venv/bin/activate
        if python3 -c "import boto3, colorama, tabulate" 2>/dev/null; then
            print_status "Dependencies installed in virtual environment" "SUCCESS"
            deactivate
            return 0
        else
            print_status "Dependencies not installed in virtual environment" "ERROR"
            print_status "Run './setup.sh' to install dependencies" "INFO"
            deactivate
            return 1
        fi
    else
        print_status "Virtual environment not found, cannot check dependencies" "ERROR"
        return 1
    fi
}

# Function to check IAM permissions
check_iam_permissions() {
    print_status "Checking IAM permissions..." "INFO"
    
    local all_permissions_good=true
    
    # Test EC2 permissions
    if aws ec2 describe-instances --max-items 1 >/dev/null 2>&1; then
        print_status "EC2 permissions: ✅ OK" "SUCCESS"
    else
        print_status "EC2 permissions: ❌ Insufficient" "ERROR"
        all_permissions_good=false
    fi
    
    # Test VPC permissions
    if aws ec2 describe-vpcs --max-items 1 >/dev/null 2>&1; then
        print_status "VPC permissions: ✅ OK" "SUCCESS"
    else
        print_status "VPC permissions: ❌ Insufficient" "ERROR"
        all_permissions_good=false
    fi
    
    # Test IAM permissions (for creating roles)
    if aws iam list-roles --max-items 1 >/dev/null 2>&1; then
        print_status "IAM permissions: ✅ OK" "SUCCESS"
    else
        print_status "IAM permissions: ❌ Insufficient" "ERROR"
        all_permissions_good=false
    fi
    
    # Test Security Group permissions
    if aws ec2 describe-security-groups --max-items 1 >/dev/null 2>&1; then
        print_status "Security Group permissions: ✅ OK" "SUCCESS"
    else
        print_status "Security Group permissions: ❌ Insufficient" "ERROR"
        all_permissions_good=false
    fi
    
    if [ "$all_permissions_good" = false ]; then
        echo ""
        print_status "Insufficient IAM permissions detected." "ERROR"
        print_status "Your AWS user/role needs the following permissions:" "INFO"
        echo ""
        echo "Required permissions:"
        echo "  - ec2:* (for VPC, instances, security groups, key pairs)"
        echo "  - iam:* (for creating roles and instance profiles)"
        echo "  - ssm:* (for Systems Manager Session Manager)"
        echo ""
        print_status "You can create an IAM policy with these permissions and attach it to your user/role." "INFO"
        return 1
    else
        print_status "All required IAM permissions are available" "SUCCESS"
        return 0
    fi
}

# Function to install Python dependencies
install_dependencies() {
    print_status "Installing Python dependencies..." "INFO"
    
    if command_exists pip3; then
        pip3 install -r requirements.txt
        print_status "Dependencies installed successfully" "SUCCESS"
    elif command_exists pip; then
        pip install -r requirements.txt
        print_status "Dependencies installed successfully" "SUCCESS"
    else
        print_status "pip not found. Please install pip." "ERROR"
        return 1
    fi
}

# Function to create virtual environment
create_virtual_env() {
    if [ "$1" = "--venv" ]; then
        print_status "Creating Python virtual environment..." "INFO"
        
        if command_exists python3; then
            python3 -m venv venv
            print_status "Virtual environment created: venv/" "SUCCESS"
            print_status "To activate: source venv/bin/activate" "INFO"
            print_status "To deactivate: deactivate" "INFO"
        else
            print_status "Python 3 not found. Cannot create virtual environment." "ERROR"
            return 1
        fi
    fi
}

# Function to display usage information
show_usage() {
    echo -e "${CYAN}AWS VPC Security Architecture Lab Automation - Setup${NC}"
    echo "=================================================="
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --check-only    Only check prerequisites (don't install)"
    echo "  --help          Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0              # Setup with virtual environment"
    echo "  $0 --check-only # Only check if everything is ready"
    echo ""
}

# Function to display next steps
show_next_steps() {
    echo ""
    print_status "Next Steps:" "HEADER"
    
    echo "1. Activate the virtual environment:"
    echo "   source venv/bin/activate"
    echo ""
    echo "2. Run the VPC automation:"
    echo "   ./run_vpc_automation.sh  # Recommended (handles venv activation)"
    echo "   # OR manually:"
    echo "   source venv/bin/activate"
    echo "   python3 vpc_automation.py"
    echo ""
    echo "3. Test connectivity:"
    echo "   python3 test_connection.py"
    echo ""
    echo "4. Clean up resources when done:"
    echo "   python3 cleanup.py"
    echo ""
    echo "5. Deactivate virtual environment when done:"
    echo "   deactivate"
    
    echo ""
    print_status "Happy Learning! 🚀" "SUCCESS"
}

# Main setup function
main_setup() {
    print_status "AWS VPC Security Architecture Lab Automation - Setup" "HEADER"
    echo "=================================================="
    echo ""
    
    # Check prerequisites
    print_status "Checking prerequisites..." "INFO"
    
    local all_good=true
    
    # Check Python
    if ! check_python_version; then
        all_good=false
    fi
    
    # Check aws.cfg file for placeholder values if in check-only mode
    if [ "$1" = "--check-only" ] && [ -f "aws.cfg" ]; then
        echo ""
        print_status "Checking aws.cfg file..." "INFO"
        
        # Read values from aws.cfg using grep and cut
        local access_key=$(grep "^access_key_id" aws.cfg | cut -d'=' -f2 | tr -d ' ')
        local secret_key=$(grep "^secret_access_key" aws.cfg | cut -d'=' -f2 | tr -d ' ')
        local region=$(grep "^region" aws.cfg | cut -d'=' -f2 | tr -d ' ')
        
        # Check for placeholder values
        if [ "$access_key" = "YOUR_ACCESS_KEY_ID_HERE" ] || [ -z "$access_key" ]; then
            print_status "Please update 'access_key_id' in aws.cfg file with your AWS Access Key ID" "ERROR"
            all_good=false
        fi
        
        if [ "$secret_key" = "YOUR_SECRET_ACCESS_KEY_HERE" ] || [ -z "$secret_key" ]; then
            print_status "Please update 'secret_access_key' in aws.cfg file with your AWS Secret Access Key" "ERROR"
            all_good=false
        fi
        
        if [ "$region" = "YOUR_REGION_HERE" ] || [ -z "$region" ]; then
            print_status "Please update 'region' in aws.cfg file with your AWS region (e.g., us-east-1)" "ERROR"
            all_good=false
        fi
        
        if [ "$all_good" = false ]; then
            echo ""
            print_status "📖 Need help getting AWS credentials?" "INFO"
            print_status "See AWS-SETUP-GUIDE.md for detailed instructions" "INFO"
            print_status "After updating aws.cfg, run './setup.sh' again" "INFO"
        else
            print_status "aws.cfg file is properly configured" "SUCCESS"
        fi
    fi
    
    # Check AWS CLI
    if ! check_aws_cli "$1"; then
        all_good=false
    fi
    
    # Check AWS credentials
    if ! check_aws_credentials "$1"; then
        all_good=false
    fi
    
    # Check IAM permissions only if AWS credentials are configured
    if command_exists aws && aws sts get-caller-identity >/dev/null 2>&1; then
        if ! check_iam_permissions; then
            all_good=false
        fi
    fi
    
    # For check-only mode, continue to project setup check even if prerequisites fail
    if [ "$1" = "--check-only" ]; then
        if [ "$all_good" = false ]; then
            print_status "System prerequisites check failed." "WARNING"
        else
            print_status "System prerequisites are satisfied!" "SUCCESS"
        fi
        
        echo ""
        print_status "Checking project setup..." "INFO"
        
        local project_good=true
        
        # Check virtual environment
        if ! check_virtual_env; then
            project_good=false
        fi
        
        # Check dependencies (only if virtual environment exists)
        if [ -d "venv" ]; then
            if ! check_dependencies; then
                project_good=false
            fi
        fi
        
        if [ "$project_good" = false ]; then
            print_status "Project setup check failed. Please run './setup.sh' to fix the issues above." "ERROR"
            exit 1
        fi
        
        print_status "All checks passed! Project is ready to use." "SUCCESS"
        exit 0
    fi
    
    # For full setup mode, exit if prerequisites fail
    if [ "$all_good" = false ]; then
        print_status "Prerequisites check failed. Please fix the issues above." "ERROR"
        exit 1
    fi
    
    print_status "All prerequisites are satisfied!" "SUCCESS"
    
    # Install dependencies in virtual environment (always recommended)
    echo ""
    create_virtual_env "--venv"
    
    # Install dependencies in virtual environment
    echo ""
    print_status "Installing dependencies in virtual environment..." "INFO"
    source venv/bin/activate
    pip install -r requirements.txt
    print_status "Dependencies installed successfully in virtual environment" "SUCCESS"
    deactivate
    
    # Show next steps
    show_next_steps "$1"
}

# Parse command line arguments
case "${1:-}" in
    --help)
        show_usage
        exit 0
        ;;
    --check-only)
        main_setup "$1"
        ;;
    "")
        main_setup
        ;;
    *)
        print_status "Unknown option: $1" "ERROR"
        show_usage
        exit 1
        ;;
esac
