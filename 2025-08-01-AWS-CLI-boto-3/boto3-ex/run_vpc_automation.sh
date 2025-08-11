#!/bin/bash

# VPC Automation Wrapper Script
# This script activates the virtual environment and runs the VPC automation

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

# Function to check if virtual environment exists
check_virtual_env() {
    if [ -d "venv" ] && [ -f "venv/bin/activate" ]; then
        return 0
    else
        return 1
    fi
}

# Function to check if dependencies are installed
check_dependencies() {
    source venv/bin/activate
    if python3 -c "import boto3, colorama, tabulate" 2>/dev/null; then
        deactivate
        return 0
    else
        deactivate
        return 1
    fi
}

# Main function
main() {
    print_status "VPC Automation Wrapper" "HEADER"
    echo "=================================================="
    echo ""
    
    # Check if virtual environment exists
    if ! check_virtual_env; then
        print_status "Virtual environment not found." "ERROR"
        print_status "Please run './setup.sh' first to set up the environment." "INFO"
        exit 1
    fi
    
    # Check if dependencies are installed
    if ! check_dependencies; then
        print_status "Dependencies not found in virtual environment." "ERROR"
        print_status "Please run './setup.sh' first to install dependencies." "INFO"
        exit 1
    fi
    
    print_status "Virtual environment and dependencies verified." "SUCCESS"
    echo ""
    
    # Activate virtual environment and run automation
    print_status "Activating virtual environment..." "INFO"
    source venv/bin/activate
    
    print_status "Running VPC automation..." "INFO"
    echo ""
    
    # Run the VPC automation
    python3 vpc_automation.py
    
    # Deactivate virtual environment
    deactivate
    
    print_status "VPC automation completed." "SUCCESS"
    print_status "Virtual environment deactivated." "INFO"
}

# Show usage information
show_usage() {
    echo -e "${CYAN}VPC Automation Wrapper${NC}"
    echo "=================================================="
    echo ""
    echo "Usage: $0"
    echo ""
    echo "This script will:"
    echo "  1. Check if virtual environment exists"
    echo "  2. Verify dependencies are installed"
    echo "  3. Activate virtual environment"
    echo "  4. Run VPC automation"
    echo "  5. Deactivate virtual environment"
    echo ""
    echo "Prerequisites:"
    echo "  - Run './setup.sh' first to set up the environment"
    echo ""
}

# Parse command line arguments
case "${1:-}" in
    --help|-h)
        show_usage
        exit 0
        ;;
    "")
        main
        ;;
    *)
        print_status "Unknown option: $1" "ERROR"
        show_usage
        exit 1
        ;;
esac
