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

# Function to check AWS CLI
check_aws_cli() {
    if command_exists aws; then
        aws_version=$(aws --version 2>&1 | awk '{print $1}')
        print_status "Found $aws_version" "SUCCESS"
        return 0
    else
        print_status "AWS CLI not found. Please install AWS CLI v2." "ERROR"
        print_status "Visit: https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html" "INFO"
        return 1
    fi
}

# Function to check AWS credentials
check_aws_credentials() {
    if aws sts get-caller-identity >/dev/null 2>&1; then
        identity=$(aws sts get-caller-identity --query 'Arn' --output text)
        print_status "AWS credentials configured: $identity" "SUCCESS"
        return 0
    else
        print_status "AWS credentials not configured or invalid." "ERROR"
        print_status "Please run 'aws configure' to set up your credentials." "INFO"
        return 1
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
    echo "  --venv          Create Python virtual environment"
    echo "  --check-only    Only check prerequisites (don't install)"
    echo "  --help          Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0              # Basic setup"
    echo "  $0 --venv       # Setup with virtual environment"
    echo "  $0 --check-only # Only check if everything is ready"
    echo ""
}

# Function to display next steps
show_next_steps() {
    echo ""
    print_status "Next Steps:" "HEADER"
    echo "1. Run the VPC automation:"
    echo "   python3 vpc_automation.py"
    echo ""
    echo "2. Test connectivity:"
    echo "   python3 test_connection.py"
    echo ""
    echo "3. Clean up resources when done:"
    echo "   python3 cleanup.py"
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
    
    # Check AWS CLI
    if ! check_aws_cli; then
        all_good=false
    fi
    
    # Check AWS credentials
    if ! check_aws_credentials; then
        all_good=false
    fi
    
    if [ "$all_good" = false ]; then
        print_status "Prerequisites check failed. Please fix the issues above." "ERROR"
        exit 1
    fi
    
    print_status "All prerequisites are satisfied!" "SUCCESS"
    
    # Install dependencies if not check-only
    if [ "$1" != "--check-only" ]; then
        echo ""
        install_dependencies
    fi
    
    # Create virtual environment if requested
    if [ "$1" = "--venv" ]; then
        echo ""
        create_virtual_env "$1"
    fi
    
    # Show next steps
    show_next_steps
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
    --venv)
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
