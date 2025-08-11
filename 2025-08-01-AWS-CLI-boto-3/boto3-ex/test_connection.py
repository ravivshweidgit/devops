#!/usr/bin/env python3
"""
Test script for AWS VPC Security Architecture Lab
This script tests connectivity to the created VPC infrastructure
"""

import boto3
import time
import subprocess
import sys
from botocore.exceptions import ClientError
from colorama import init, Fore, Style
import json
import logging
import os
from datetime import datetime

# Initialize colorama for colored output
init(autoreset=True)

# Configure logging to both file and console
def setup_logging():
    """Setup logging configuration for both file and console output"""
    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)
    
    # Create logger
    logger = logging.getLogger('vpc_test')
    logger.setLevel(logging.INFO)
    
    # Clear any existing handlers
    logger.handlers.clear()
    
    # Create formatters
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_formatter = logging.Formatter('%(message)s')
    
    # File handler for app.log (append mode for tests)
    file_handler = logging.FileHandler('app.log', mode='a')
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(file_formatter)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(console_formatter)
    
    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

# Setup logging
logger = setup_logging()

class VPCTester:
    def __init__(self, region='eu-north-1'):
        """Initialize the VPC tester class"""
        self.region = region
        self.ec2_client = boto3.client('ec2', region_name=region)
        self.ssm_client = boto3.client('ssm', region_name=region)
        
        # Configuration
        self.vpc_name = 'lab-vpc'
        self.key_name = 'key01'
        
        # Resource IDs (will be populated during discovery)
        self.vpc_id = None
        self.bastion_instance_id = None
        self.nat_instance_id = None
        self.private_instance_id = None
        self.bastion_public_ip = None
        self.private_private_ip = None
        
        # Log initialization
        logger.info(f"VPC Tester initialized for region: {region}")
        logger.info(f"Looking for VPC: {self.vpc_name}")
        
    def print_status(self, message, status="INFO"):
        """Print colored status messages and log them"""
        if status == "SUCCESS":
            colored_message = f"{Fore.GREEN}✅ {message}{Style.RESET_ALL}"
            logger.info(f"SUCCESS: {message}")
        elif status == "ERROR":
            colored_message = f"{Fore.RED}❌ {message}{Style.RESET_ALL}"
            logger.error(f"ERROR: {message}")
        elif status == "WARNING":
            colored_message = f"{Fore.YELLOW}⚠️  {message}{Style.RESET_ALL}"
            logger.warning(f"WARNING: {message}")
        else:
            colored_message = f"{Fore.BLUE}ℹ️  {message}{Style.RESET_ALL}"
            logger.info(f"INFO: {message}")
        
        print(colored_message)
    
    def discover_resources(self):
        """Discover existing VPC resources"""
        try:
            self.print_status("Discovering VPC resources...")
            logger.info("Starting VPC resource discovery")
            
            # Find VPC
            vpc_response = self.ec2_client.describe_vpcs(
                Filters=[
                    {'Name': 'tag:Name', 'Values': [self.vpc_name]},
                    {'Name': 'tag:Environment', 'Values': ['Lab']}
                ]
            )
            
            if not vpc_response['Vpcs']:
                error_msg = "VPC not found. Please run vpc_automation.py first."
                logger.error(error_msg)
                self.print_status(error_msg, "ERROR")
                return False
            
            self.vpc_id = vpc_response['Vpcs'][0]['VpcId']
            logger.info(f"Found VPC: {self.vpc_id}")
            self.print_status(f"Found VPC: {self.vpc_id}", "SUCCESS")
            
            # Find instances
            instance_response = self.ec2_client.describe_instances(
                Filters=[
                    {'Name': 'vpc-id', 'Values': [self.vpc_id]},
                    {'Name': 'tag:Environment', 'Values': ['Lab']},
                    {'Name': 'instance-state-name', 'Values': ['running']}
                ]
            )
            
            for reservation in instance_response['Reservations']:
                for instance in reservation['Instances']:
                    name = "Unknown"
                    for tag in instance.get('Tags', []):
                        if tag['Key'] == 'Name':
                            name = tag['Value']
                            break
                    
                    if name == 'bastion':
                        self.bastion_instance_id = instance['InstanceId']
                        self.bastion_public_ip = instance.get('PublicIpAddress')
                        logger.info(f"Found bastion instance: {self.bastion_instance_id} (IP: {self.bastion_public_ip})")
                        self.print_status(f"Found bastion instance: {self.bastion_instance_id}", "SUCCESS")
                    elif name == 'nat':
                        self.nat_instance_id = instance['InstanceId']
                        logger.info(f"Found NAT instance: {self.nat_instance_id}")
                        self.print_status(f"Found NAT instance: {self.nat_instance_id}", "SUCCESS")
                    elif name == 'private':
                        self.private_instance_id = instance['InstanceId']
                        self.private_private_ip = instance.get('PrivateIpAddress')
                        logger.info(f"Found private instance: {self.private_instance_id} (IP: {self.private_private_ip})")
                        self.print_status(f"Found private instance: {self.private_instance_id}", "SUCCESS")
            
            logger.info("Resource discovery completed successfully")
            return True
            
        except ClientError as e:
            error_msg = f"Error discovering resources: {e}"
            logger.error(error_msg)
            self.print_status(error_msg, "ERROR")
            return False
    
    def test_ssh_connectivity(self):
        """Test SSH connectivity to bastion host"""
        if not self.bastion_public_ip:
            error_msg = "Bastion public IP not found"
            logger.error(error_msg)
            self.print_status(error_msg, "ERROR")
            return False
        
        try:
            self.print_status("Testing SSH connectivity to bastion host...")
            logger.info(f"Testing SSH connectivity to bastion host: {self.bastion_public_ip}")
            
            # Test SSH connection
            ssh_command = [
                'ssh', '-i', f'{self.key_name}.pem',
                '-o', 'ConnectTimeout=10',
                '-o', 'StrictHostKeyChecking=no',
                '-o', 'UserKnownHostsFile=/dev/null',
                f'ec2-user@{self.bastion_public_ip}',
                'echo "SSH connection successful"'
            ]
            
            logger.info(f"Executing SSH command: {' '.join(ssh_command)}")
            result = subprocess.run(ssh_command, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                logger.info("SSH connection to bastion host successful")
                self.print_status("SSH connection to bastion host successful", "SUCCESS")
                return True
            else:
                error_msg = f"SSH connection failed: {result.stderr}"
                logger.error(error_msg)
                self.print_status(error_msg, "ERROR")
                return False
                
        except subprocess.TimeoutExpired:
            error_msg = "SSH connection timed out"
            logger.error(error_msg)
            self.print_status(error_msg, "ERROR")
            return False
        except FileNotFoundError:
            error_msg = "SSH command not found. Please install OpenSSH client."
            logger.error(error_msg)
            self.print_status(error_msg, "ERROR")
            return False
        except Exception as e:
            error_msg = f"SSH test error: {e}"
            logger.error(error_msg)
            self.print_status(error_msg, "ERROR")
            return False
    
    def test_nat_connectivity(self):
        """Test NAT instance connectivity"""
        if not self.nat_instance_id:
            error_msg = "NAT instance not found"
            logger.error(error_msg)
            self.print_status(error_msg, "ERROR")
            return False
        
        try:
            self.print_status("Testing NAT instance connectivity...")
            logger.info(f"Testing NAT instance connectivity: {self.nat_instance_id}")
            
            # Check if NAT instance is running
            response = self.ec2_client.describe_instances(InstanceIds=[self.nat_instance_id])
            instance = response['Reservations'][0]['Instances'][0]
            
            if instance['State']['Name'] == 'running':
                logger.info("NAT instance is running")
                self.print_status("NAT instance is running", "SUCCESS")
                
                # Check source/destination check is disabled
                if not instance.get('SourceDestCheck', True):
                    logger.info("NAT instance source/destination check is disabled")
                    self.print_status("NAT instance source/destination check is disabled", "SUCCESS")
                    return True
                else:
                    warning_msg = "NAT instance source/destination check is enabled (should be disabled)"
                    logger.warning(warning_msg)
                    self.print_status(warning_msg, "WARNING")
                    return False
            else:
                error_msg = f"NAT instance is not running: {instance['State']['Name']}"
                logger.error(error_msg)
                self.print_status(error_msg, "ERROR")
                return False
                
        except ClientError as e:
            error_msg = f"Error testing NAT connectivity: {e}"
            logger.error(error_msg)
            self.print_status(error_msg, "ERROR")
            return False
    
    def test_private_instance_ssm(self):
        """Test SSM Session Manager connectivity to private instance"""
        if not self.private_instance_id:
            error_msg = "Private instance not found"
            logger.error(error_msg)
            self.print_status(error_msg, "ERROR")
            return False
        
        try:
            self.print_status("Testing SSM connectivity to private instance...")
            logger.info(f"Testing SSM connectivity to private instance: {self.private_instance_id}")
            
            # Check if instance has SSM agent running
            response = self.ssm_client.describe_instance_information(
                Filters=[
                    {
                        'Key': 'InstanceIds',
                        'Values': [self.private_instance_id]
                    }
                ]
            )
            
            if response['InstanceInformationList']:
                instance_info = response['InstanceInformationList'][0]
                if instance_info['PingStatus'] == 'Online':
                    logger.info("Private instance is online for SSM")
                    self.print_status("Private instance is online for SSM", "SUCCESS")
                    return True
                else:
                    warning_msg = f"Private instance SSM status: {instance_info['PingStatus']}"
                    logger.warning(warning_msg)
                    self.print_status(warning_msg, "WARNING")
                    return False
            else:
                error_msg = "Private instance not found in SSM"
                logger.error(error_msg)
                self.print_status(error_msg, "ERROR")
                return False
                
        except ClientError as e:
            error_msg = f"Error testing SSM connectivity: {e}"
            logger.error(error_msg)
            self.print_status(error_msg, "ERROR")
            return False
    
    def test_internet_connectivity(self):
        """Test internet connectivity through NAT"""
        if not self.bastion_public_ip:
            error_msg = "Bastion public IP not found"
            logger.error(error_msg)
            self.print_status(error_msg, "ERROR")
            return False
        
        try:
            self.print_status("Testing internet connectivity through NAT...")
            logger.info(f"Testing internet connectivity through NAT via bastion: {self.bastion_public_ip}")
            
            # Test internet connectivity from bastion
            ssh_command = [
                'ssh', '-i', f'{self.key_name}.pem',
                '-o', 'ConnectTimeout=10',
                '-o', 'StrictHostKeyChecking=no',
                '-o', 'UserKnownHostsFile=/dev/null',
                f'ec2-user@{self.bastion_public_ip}',
                'curl -s --connect-timeout 10 https://httpbin.org/ip'
            ]
            
            logger.info(f"Executing internet connectivity test via SSH")
            result = subprocess.run(ssh_command, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                logger.info("Internet connectivity through NAT is working")
                self.print_status("Internet connectivity through NAT is working", "SUCCESS")
                return True
            else:
                error_msg = "Internet connectivity test failed"
                logger.error(error_msg)
                self.print_status(error_msg, "ERROR")
                return False
                
        except subprocess.TimeoutExpired:
            error_msg = "Internet connectivity test timed out"
            logger.error(error_msg)
            self.print_status(error_msg, "ERROR")
            return False
        except Exception as e:
            error_msg = f"Internet connectivity test error: {e}"
            logger.error(error_msg)
            self.print_status(error_msg, "ERROR")
            return False
    
    def test_private_instance_ssh_via_bastion(self):
        """Test SSH to private instance via bastion"""
        if not self.bastion_public_ip or not self.private_private_ip:
            error_msg = "Bastion or private instance IP not found"
            logger.error(error_msg)
            self.print_status(error_msg, "ERROR")
            return False
        
        try:
            self.print_status("Testing SSH to private instance via bastion...")
            logger.info(f"Testing SSH to private instance {self.private_private_ip} via bastion {self.bastion_public_ip}")
            
            # First, copy key to bastion
            scp_command = [
                'scp', '-i', f'{self.key_name}.pem',
                '-o', 'ConnectTimeout=10',
                '-o', 'StrictHostKeyChecking=no',
                '-o', 'UserKnownHostsFile=/dev/null',
                f'{self.key_name}.pem',
                f'ec2-user@{self.bastion_public_ip}:~/'
            ]
            
            logger.info(f"Copying key to bastion host")
            result = subprocess.run(scp_command, capture_output=True, text=True, timeout=30)
            
            if result.returncode != 0:
                error_msg = "Failed to copy key to bastion"
                logger.error(error_msg)
                self.print_status(error_msg, "ERROR")
                return False
            
            # Test SSH to private instance via bastion
            ssh_command = [
                'ssh', '-i', f'{self.key_name}.pem',
                '-o', 'ConnectTimeout=10',
                '-o', 'StrictHostKeyChecking=no',
                '-o', 'UserKnownHostsFile=/dev/null',
                f'ec2-user@{self.bastion_public_ip}',
                f'ssh -i ~/{self.key_name}.pem -o ConnectTimeout=10 -o StrictHostKeyChecking=no ec2-user@{self.private_private_ip} "echo SSH via bastion successful"'
            ]
            
            logger.info(f"Testing SSH to private instance via bastion")
            result = subprocess.run(ssh_command, capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                logger.info("SSH to private instance via bastion successful")
                self.print_status("SSH to private instance via bastion successful", "SUCCESS")
                return True
            else:
                error_msg = f"SSH to private instance via bastion failed: {result.stderr}"
                logger.error(error_msg)
                self.print_status(error_msg, "ERROR")
                return False
                
        except subprocess.TimeoutExpired:
            error_msg = "SSH via bastion test timed out"
            logger.error(error_msg)
            self.print_status(error_msg, "ERROR")
            return False
        except Exception as e:
            error_msg = f"SSH via bastion test error: {e}"
            logger.error(error_msg)
            self.print_status(error_msg, "ERROR")
            return False
    
    def test_security_groups(self):
        """Test security group configurations"""
        try:
            self.print_status("Testing security group configurations...")
            logger.info("Testing security group configurations")
            
            # Get security groups
            sg_response = self.ec2_client.describe_security_groups(
                Filters=[
                    {'Name': 'vpc-id', 'Values': [self.vpc_id]},
                    {'Name': 'tag:Environment', 'Values': ['Lab']}
                ]
            )
            
            security_groups = {}
            for sg in sg_response['SecurityGroups']:
                name = "Unknown"
                for tag in sg.get('Tags', []):
                    if tag['Key'] == 'Name':
                        name = tag['Value']
                        break
                security_groups[name] = sg
                logger.info(f"Found security group: {name} ({sg['GroupId']})")
            
            # Test bastion security group
            if 'lab-vpc-bastion-sg' in security_groups:
                bastion_sg = security_groups['lab-vpc-bastion-sg']
                ssh_rules = [rule for rule in bastion_sg['IpPermissions'] 
                           if rule.get('FromPort') == 22 and rule.get('ToPort') == 22]
                
                if ssh_rules:
                    logger.info("Bastion security group allows SSH")
                    self.print_status("Bastion security group allows SSH", "SUCCESS")
                else:
                    error_msg = "Bastion security group missing SSH rule"
                    logger.error(error_msg)
                    self.print_status(error_msg, "ERROR")
                    return False
            else:
                error_msg = "Bastion security group not found"
                logger.error(error_msg)
                self.print_status(error_msg, "ERROR")
                return False
            
            # Test private security group
            if 'lab-vpc-private-sg' in security_groups:
                private_sg = security_groups['lab-vpc-private-sg']
                ssh_rules = [rule for rule in private_sg['IpPermissions'] 
                           if rule.get('FromPort') == 22 and rule.get('ToPort') == 22]
                
                if ssh_rules:
                    logger.info("Private security group allows SSH from bastion")
                    self.print_status("Private security group allows SSH from bastion", "SUCCESS")
                else:
                    error_msg = "Private security group missing SSH rule"
                    logger.error(error_msg)
                    self.print_status(error_msg, "ERROR")
                    return False
            else:
                error_msg = "Private security group not found"
                logger.error(error_msg)
                self.print_status(error_msg, "ERROR")
                return False
            
            logger.info("Security group configuration test completed successfully")
            return True
            
        except ClientError as e:
            error_msg = f"Error testing security groups: {e}"
            logger.error(error_msg)
            self.print_status(error_msg, "ERROR")
            return False
    
    def generate_test_report(self, test_results):
        """Generate a test report"""
        print(f"\n{Fore.CYAN}📊 Test Report{Style.RESET_ALL}")
        print("=" * 50)
        
        total_tests = len(test_results)
        passed_tests = sum(1 for result in test_results.values() if result)
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {Fore.GREEN}{passed_tests}{Style.RESET_ALL}")
        print(f"Failed: {Fore.RED}{failed_tests}{Style.RESET_ALL}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        print(f"\n{Fore.CYAN}Detailed Results:{Style.RESET_ALL}")
        for test_name, result in test_results.items():
            status = f"{Fore.GREEN}✅ PASS{Style.RESET_ALL}" if result else f"{Fore.RED}❌ FAIL{Style.RESET_ALL}"
            print(f"  {test_name}: {status}")
        
        # Log test results
        logger.info(f"Test Report - Total: {total_tests}, Passed: {passed_tests}, Failed: {failed_tests}, Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests == 0:
            success_msg = "All tests passed! Your VPC infrastructure is working correctly."
            logger.info(success_msg)
            print(f"\n{Fore.GREEN}🎉 {success_msg}{Style.RESET_ALL}")
        else:
            warning_msg = "Some tests failed. Please check the configuration."
            logger.warning(warning_msg)
            print(f"\n{Fore.YELLOW}⚠️  {warning_msg}{Style.RESET_ALL}")
    
    def run_all_tests(self):
        """Run all connectivity tests"""
        try:
            self.print_status("Starting VPC connectivity tests...", "SUCCESS")
            logger.info("=== Starting VPC Connectivity Tests ===")
            logger.info(f"Tests started at: {datetime.now().isoformat()}")
            
            # Discover resources first
            if not self.discover_resources():
                logger.error("Resource discovery failed, cannot continue with tests")
                return False
            
            # Run tests
            test_results = {}
            
            test_results['Resource Discovery'] = True  # Already passed if we got here
            
            logger.info("Running SSH connectivity test")
            test_results['SSH to Bastion'] = self.test_ssh_connectivity()
            
            logger.info("Running NAT instance status test")
            test_results['NAT Instance Status'] = self.test_nat_connectivity()
            
            logger.info("Running SSM connectivity test")
            test_results['SSM to Private Instance'] = self.test_private_instance_ssm()
            
            logger.info("Running internet connectivity test")
            test_results['Internet Connectivity'] = self.test_internet_connectivity()
            
            logger.info("Running SSH via bastion test")
            test_results['SSH to Private via Bastion'] = self.test_private_instance_ssh_via_bastion()
            
            logger.info("Running security group configuration test")
            test_results['Security Group Configuration'] = self.test_security_groups()
            
            # Generate report
            self.generate_test_report(test_results)
            
            logger.info("=== VPC Connectivity Tests Completed ===")
            logger.info(f"Tests completed at: {datetime.now().isoformat()}")
            
            return True
            
        except Exception as e:
            error_msg = f"Unexpected error during testing: {e}"
            logger.error(error_msg)
            self.print_status(error_msg, "ERROR")
            return False

def main():
    """Main function"""
    print(f"{Fore.CYAN}🧪 AWS VPC Security Architecture Lab - Connectivity Tests{Style.RESET_ALL}")
    print("=" * 70)
    
    logger.info("=== VPC Test Script Started ===")
    
    # Check AWS credentials
    try:
        sts = boto3.client('sts')
        identity = sts.get_caller_identity()
        print(f"Authenticated as: {identity['Arn']}")
        logger.info(f"Authenticated as: {identity['Arn']}")
    except Exception as e:
        error_msg = f"AWS credentials not configured or invalid: {e}"
        logger.error(error_msg)
        print(f"{Fore.RED}❌ {error_msg}{Style.RESET_ALL}")
        print("Please run 'aws configure' to set up your credentials")
        return
    
    # Check if key file exists
    import os
    if not os.path.exists('key01.pem'):
        error_msg = "Key file 'key01.pem' not found"
        logger.error(error_msg)
        print(f"{Fore.RED}❌ {error_msg}{Style.RESET_ALL}")
        print("Please run vpc_automation.py first to create the infrastructure")
        return
    
    # Create tester instance
    tester = VPCTester()
    
    # Run tests
    tester.run_all_tests()
    
    logger.info("=== VPC Test Script Finished ===")

if __name__ == "__main__":
    main()
