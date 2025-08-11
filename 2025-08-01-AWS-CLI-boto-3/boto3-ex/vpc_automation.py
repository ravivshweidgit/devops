#!/usr/bin/env python3
"""
AWS VPC Security Architecture Lab Automation
This script automates the complete setup of a VPC with bastion host, NAT instance, and private instance
"""

import boto3
import time
import json
import os
from botocore.exceptions import ClientError, WaiterError
from colorama import init, Fore, Style
import logging
from datetime import datetime

# Initialize colorama for colored output
init(autoreset=True)

# Configure logging to both file and console
def setup_logging():
    """Setup logging configuration for both file and console output"""
    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)
    
    # Create logger
    logger = logging.getLogger('vpc_automation')
    logger.setLevel(logging.INFO)
    
    # Clear any existing handlers
    logger.handlers.clear()
    
    # Create formatters
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_formatter = logging.Formatter('%(message)s')
    
    # File handler for app.log
    file_handler = logging.FileHandler('app.log', mode='w')
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

class VPCAutomation:
    def __init__(self, region='eu-north-1'):
        """Initialize the VPC automation class"""
        self.region = region
        self.ec2_client = boto3.client('ec2', region_name=region)
        self.ec2_resource = boto3.resource('ec2', region_name=region)
        self.iam_client = boto3.client('iam')
        
        # Configuration
        self.vpc_name = 'lab-vpc'
        self.vpc_cidr = '10.0.0.0/16'
        self.public_subnet_cidr = '10.0.1.0/24'
        self.private_subnet_cidr = '10.0.2.0/24'
        self.key_name = 'key01'
        
        # Resource IDs (will be populated during creation)
        self.vpc_id = None
        self.internet_gateway_id = None
        self.public_subnet_id = None
        self.private_subnet_id = None
        self.public_route_table_id = None
        self.private_route_table_id = None
        self.bastion_sg_id = None
        self.nat_sg_id = None
        self.private_sg_id = None
        self.bastion_instance_id = None
        self.nat_instance_id = None
        self.private_instance_id = None
        
        # Log initialization
        logger.info(f"VPC Automation initialized for region: {region}")
        logger.info(f"VPC Name: {self.vpc_name}, CIDR: {self.vpc_cidr}")
        
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
    
    def wait_for_instance_running(self, instance_id, timeout=300):
        """Wait for instance to be running"""
        try:
            logger.info(f"Waiting for instance {instance_id} to be running (timeout: {timeout}s)")
            waiter = self.ec2_client.get_waiter('instance_running')
            waiter.wait(InstanceIds=[instance_id], WaiterConfig={'Delay': 10, 'MaxAttempts': timeout//10})
            logger.info(f"Instance {instance_id} is now running")
            return True
        except WaiterError as e:
            error_msg = f"Instance {instance_id} failed to start within {timeout} seconds"
            logger.error(f"{error_msg}: {e}")
            self.print_status(error_msg, "ERROR")
            return False
    
    def create_vpc(self):
        """Create VPC with internet gateway"""
        try:
            self.print_status("Creating VPC...")
            logger.info("Starting VPC creation process")
            
            # Create VPC
            vpc_response = self.ec2_client.create_vpc(
                CidrBlock=self.vpc_cidr,
                EnableDnsHostnames=True,
                EnableDnsSupport=True,
                TagSpecifications=[
                    {
                        'ResourceType': 'vpc',
                        'Tags': [
                            {'Key': 'Name', 'Value': self.vpc_name},
                            {'Key': 'Environment', 'Value': 'Lab'}
                        ]
                    }
                ]
            )
            self.vpc_id = vpc_response['Vpc']['VpcId']
            logger.info(f"VPC created successfully: {self.vpc_id}")
            self.print_status(f"VPC created: {self.vpc_id}", "SUCCESS")
            
            # Create Internet Gateway
            igw_response = self.ec2_client.create_internet_gateway(
                TagSpecifications=[
                    {
                        'ResourceType': 'internet-gateway',
                        'Tags': [
                            {'Key': 'Name', 'Value': f'{self.vpc_name}-igw'},
                            {'Key': 'Environment', 'Value': 'Lab'}
                        ]
                    }
                ]
            )
            self.internet_gateway_id = igw_response['InternetGateway']['InternetGatewayId']
            logger.info(f"Internet Gateway created: {self.internet_gateway_id}")
            self.print_status(f"Internet Gateway created: {self.internet_gateway_id}", "SUCCESS")
            
            # Attach Internet Gateway to VPC
            self.ec2_client.attach_internet_gateway(
                InternetGatewayId=self.internet_gateway_id,
                VpcId=self.vpc_id
            )
            logger.info(f"Internet Gateway {self.internet_gateway_id} attached to VPC {self.vpc_id}")
            self.print_status("Internet Gateway attached to VPC", "SUCCESS")
            
            return True
            
        except ClientError as e:
            error_msg = f"Error creating VPC: {e}"
            logger.error(error_msg)
            self.print_status(error_msg, "ERROR")
            return False
    
    def create_subnets(self):
        """Create public and private subnets"""
        try:
            self.print_status("Creating subnets...")
            logger.info("Starting subnet creation process")
            
            # Get availability zones
            azs = self.ec2_client.describe_availability_zones()
            az = azs['AvailabilityZones'][0]['ZoneName']
            logger.info(f"Using availability zone: {az}")
            
            # Create public subnet
            public_subnet_response = self.ec2_client.create_subnet(
                VpcId=self.vpc_id,
                CidrBlock=self.public_subnet_cidr,
                AvailabilityZone=az,
                MapPublicIpOnLaunch=True,
                TagSpecifications=[
                    {
                        'ResourceType': 'subnet',
                        'Tags': [
                            {'Key': 'Name', 'Value': f'{self.vpc_name}-public'},
                            {'Key': 'Environment', 'Value': 'Lab'}
                        ]
                    }
                ]
            )
            self.public_subnet_id = public_subnet_response['Subnet']['SubnetId']
            logger.info(f"Public subnet created: {self.public_subnet_id} in AZ {az}")
            self.print_status(f"Public subnet created: {self.public_subnet_id}", "SUCCESS")
            
            # Create private subnet
            private_subnet_response = self.ec2_client.create_subnet(
                VpcId=self.vpc_id,
                CidrBlock=self.private_subnet_cidr,
                AvailabilityZone=az,
                MapPublicIpOnLaunch=False,
                TagSpecifications=[
                    {
                        'ResourceType': 'subnet',
                        'Tags': [
                            {'Key': 'Name', 'Value': f'{self.vpc_name}-private'},
                            {'Key': 'Environment', 'Value': 'Lab'}
                        ]
                    }
                ]
            )
            self.private_subnet_id = private_subnet_response['Subnet']['SubnetId']
            logger.info(f"Private subnet created: {self.private_subnet_id} in AZ {az}")
            self.print_status(f"Private subnet created: {self.private_subnet_id}", "SUCCESS")
            
            return True
            
        except ClientError as e:
            error_msg = f"Error creating subnets: {e}"
            logger.error(error_msg)
            self.print_status(error_msg, "ERROR")
            return False
    
    def create_route_tables(self):
        """Create and configure route tables"""
        try:
            self.print_status("Creating route tables...")
            logger.info("Starting route table creation process")
            
            # Create public route table
            public_rt_response = self.ec2_client.create_route_table(
                VpcId=self.vpc_id,
                TagSpecifications=[
                    {
                        'ResourceType': 'route-table',
                        'Tags': [
                            {'Key': 'Name', 'Value': f'{self.vpc_name}-public-rt'},
                            {'Key': 'Environment', 'Value': 'Lab'}
                        ]
                    }
                ]
            )
            self.public_route_table_id = public_rt_response['RouteTable']['RouteTableId']
            logger.info(f"Public route table created: {self.public_route_table_id}")
            
            # Add internet gateway route to public route table
            self.ec2_client.create_route(
                RouteTableId=self.public_route_table_id,
                DestinationCidrBlock='0.0.0.0/0',
                GatewayId=self.internet_gateway_id
            )
            logger.info(f"Internet gateway route added to public route table")
            
            # Associate public subnet with public route table
            self.ec2_client.associate_route_table(
                RouteTableId=self.public_route_table_id,
                SubnetId=self.public_subnet_id
            )
            logger.info(f"Public subnet {self.public_subnet_id} associated with public route table")
            self.print_status("Public route table configured", "SUCCESS")
            
            # Create private route table
            private_rt_response = self.ec2_client.create_route_table(
                VpcId=self.vpc_id,
                TagSpecifications=[
                    {
                        'ResourceType': 'route-table',
                        'Tags': [
                            {'Key': 'Name', 'Value': f'{self.vpc_name}-private-rt'},
                            {'Key': 'Environment', 'Value': 'Lab'}
                        ]
                    }
                ]
            )
            self.private_route_table_id = private_rt_response['RouteTable']['RouteTableId']
            logger.info(f"Private route table created: {self.private_route_table_id}")
            
            # Associate private subnet with private route table
            self.ec2_client.associate_route_table(
                RouteTableId=self.private_route_table_id,
                SubnetId=self.private_subnet_id
            )
            logger.info(f"Private subnet {self.private_subnet_id} associated with private route table")
            self.print_status("Private route table configured", "SUCCESS")
            
            return True
            
        except ClientError as e:
            error_msg = f"Error creating route tables: {e}"
            logger.error(error_msg)
            self.print_status(error_msg, "ERROR")
            return False
    
    def create_security_groups(self):
        """Create security groups for bastion, NAT, and private instances"""
        try:
            self.print_status("Creating security groups...")
            logger.info("Starting security group creation process")
            
            # Create bastion security group
            bastion_sg_response = self.ec2_client.create_security_group(
                GroupName=f'{self.vpc_name}-bastion-sg',
                Description='Security group for bastion host',
                VpcId=self.vpc_id,
                TagSpecifications=[
                    {
                        'ResourceType': 'security-group',
                        'Tags': [
                            {'Key': 'Name', 'Value': f'{self.vpc_name}-bastion-sg'},
                            {'Key': 'Environment', 'Value': 'Lab'}
                        ]
                    }
                ]
            )
            self.bastion_sg_id = bastion_sg_response['GroupId']
            logger.info(f"Bastion security group created: {self.bastion_sg_id}")
            
            # Add SSH rule to bastion security group
            self.ec2_client.authorize_security_group_ingress(
                GroupId=self.bastion_sg_id,
                IpPermissions=[
                    {
                        'IpProtocol': 'tcp',
                        'FromPort': 22,
                        'ToPort': 22,
                        'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
                    }
                ]
            )
            logger.info(f"SSH rule added to bastion security group {self.bastion_sg_id}")
            self.print_status("Bastion security group created", "SUCCESS")
            
            # Create NAT security group
            nat_sg_response = self.ec2_client.create_security_group(
                GroupName=f'{self.vpc_name}-nat-sg',
                Description='Security group for NAT instance',
                VpcId=self.vpc_id,
                TagSpecifications=[
                    {
                        'ResourceType': 'security-group',
                        'Tags': [
                            {'Key': 'Name', 'Value': f'{self.vpc_name}-nat-sg'},
                            {'Key': 'Environment', 'Value': 'Lab'}
                        ]
                    }
                ]
            )
            self.nat_sg_id = nat_sg_response['GroupId']
            logger.info(f"NAT security group created: {self.nat_sg_id}")
            
            # Add rules to NAT security group
            self.ec2_client.authorize_security_group_ingress(
                GroupId=self.nat_sg_id,
                IpPermissions=[
                    {
                        'IpProtocol': '-1',
                        'IpRanges': [{'CidrIp': self.vpc_cidr}]
                    }
                ]
            )
            logger.info(f"VPC CIDR rule added to NAT security group {self.nat_sg_id}")
            self.print_status("NAT security group created", "SUCCESS")
            
            # Create private instance security group
            private_sg_response = self.ec2_client.create_security_group(
                GroupName=f'{self.vpc_name}-private-sg',
                Description='Security group for private instances',
                VpcId=self.vpc_id,
                TagSpecifications=[
                    {
                        'ResourceType': 'security-group',
                        'Tags': [
                            {'Key': 'Name', 'Value': f'{self.vpc_name}-private-sg'},
                            {'Key': 'Environment', 'Value': 'Lab'}
                        ]
                    }
                ]
            )
            self.private_sg_id = private_sg_response['GroupId']
            logger.info(f"Private security group created: {self.private_sg_id}")
            
            # Add SSH rule from bastion to private security group
            self.ec2_client.authorize_security_group_ingress(
                GroupId=self.private_sg_id,
                IpPermissions=[
                    {
                        'IpProtocol': 'tcp',
                        'FromPort': 22,
                        'ToPort': 22,
                        'UserIdGroupPairs': [{'GroupId': self.bastion_sg_id}]
                    }
                ]
            )
            logger.info(f"SSH rule from bastion added to private security group {self.private_sg_id}")
            self.print_status("Private security group created", "SUCCESS")
            
            return True
            
        except ClientError as e:
            error_msg = f"Error creating security groups: {e}"
            logger.error(error_msg)
            self.print_status(error_msg, "ERROR")
            return False
    
    def create_key_pair(self):
        """Create or verify key pair exists"""
        try:
            self.print_status(f"Checking key pair: {self.key_name}")
            logger.info(f"Checking for existing key pair: {self.key_name}")
            
            # Check if key pair exists
            try:
                self.ec2_client.describe_key_pairs(KeyNames=[self.key_name])
                logger.info(f"Key pair {self.key_name} already exists")
                self.print_status(f"Key pair {self.key_name} already exists", "SUCCESS")
                return True
            except ClientError:
                # Create new key pair
                logger.info(f"Creating new key pair: {self.key_name}")
                key_response = self.ec2_client.create_key_pair(
                    KeyName=self.key_name,
                    TagSpecifications=[
                        {
                            'ResourceType': 'key-pair',
                            'Tags': [
                                {'Key': 'Name', 'Value': self.key_name},
                                {'Key': 'Environment', 'Value': 'Lab'}
                            ]
                        }
                    ]
                )
                
                # Save private key to file
                key_file = f"{self.key_name}.pem"
                with open(key_file, 'w') as f:
                    f.write(key_response['KeyMaterial'])
                
                # Set proper permissions
                os.chmod(key_file, 0o400)
                
                logger.info(f"Key pair {self.key_name} created and saved to {key_file}")
                self.print_status(f"Key pair {self.key_name} created and saved to {key_file}", "SUCCESS")
                return True
                
        except ClientError as e:
            error_msg = f"Error with key pair: {e}"
            logger.error(error_msg)
            self.print_status(error_msg, "ERROR")
            return False
    
    def get_nat_ami(self):
        """Find NAT AMI in the region"""
        try:
            logger.info("Searching for NAT AMI in the region")
            # Search for NAT AMI
            response = self.ec2_client.describe_images(
                Owners=['amazon'],
                Filters=[
                    {'Name': 'name', 'Values': ['*nat*']},
                    {'Name': 'state', 'Values': ['available']}
                ]
            )
            
            if response['Images']:
                ami_id = response['Images'][0]['ImageId']
                logger.info(f"Found NAT AMI: {ami_id}")
                return ami_id
            else:
                # Fallback to Amazon Linux 2
                logger.info("NAT AMI not found, falling back to Amazon Linux 2")
                response = self.ec2_client.describe_images(
                    Owners=['amazon'],
                    Filters=[
                        {'Name': 'name', 'Values': ['amzn2-ami-hvm-*-x86_64-gp2']},
                        {'Name': 'state', 'Values': ['available']}
                    ]
                )
                ami_id = response['Images'][0]['ImageId']
                logger.info(f"Using Amazon Linux 2 AMI: {ami_id}")
                return ami_id
                
        except ClientError as e:
            error_msg = f"Error finding NAT AMI: {e}"
            logger.error(error_msg)
            self.print_status(error_msg, "ERROR")
            return None
    
    def create_bastion_instance(self):
        """Create bastion host instance"""
        try:
            self.print_status("Creating bastion host...")
            logger.info("Starting bastion host creation")
            
            # Get latest Amazon Linux 2 AMI
            response = self.ec2_client.describe_images(
                Owners=['amazon'],
                Filters=[
                    {'Name': 'name', 'Values': ['amzn2-ami-hvm-*-x86_64-gp2']},
                    {'Name': 'state', 'Values': ['available']}
                ]
            )
            ami_id = response['Images'][0]['ImageId']
            logger.info(f"Using AMI for bastion: {ami_id}")
            
            # Launch bastion instance
            instance_response = self.ec2_client.run_instances(
                ImageId=ami_id,
                MinCount=1,
                MaxCount=1,
                InstanceType='t2.micro',
                KeyName=self.key_name,
                SecurityGroupIds=[self.bastion_sg_id],
                SubnetId=self.public_subnet_id,
                TagSpecifications=[
                    {
                        'ResourceType': 'instance',
                        'Tags': [
                            {'Key': 'Name', 'Value': 'bastion'},
                            {'Key': 'Environment', 'Value': 'Lab'}
                        ]
                    }
                ]
            )
            
            self.bastion_instance_id = instance_response['Instances'][0]['InstanceId']
            logger.info(f"Bastion instance launched: {self.bastion_instance_id}")
            self.print_status(f"Bastion instance created: {self.bastion_instance_id}", "SUCCESS")
            
            # Wait for instance to be running
            if self.wait_for_instance_running(self.bastion_instance_id):
                self.print_status("Bastion instance is running", "SUCCESS")
                return True
            else:
                return False
                
        except ClientError as e:
            error_msg = f"Error creating bastion instance: {e}"
            logger.error(error_msg)
            self.print_status(error_msg, "ERROR")
            return False
    
    def create_nat_instance(self):
        """Create NAT instance"""
        try:
            self.print_status("Creating NAT instance...")
            logger.info("Starting NAT instance creation")
            
            # Get NAT AMI
            nat_ami = self.get_nat_ami()
            if not nat_ami:
                return False
            
            # Launch NAT instance
            instance_response = self.ec2_client.run_instances(
                ImageId=nat_ami,
                MinCount=1,
                MaxCount=1,
                InstanceType='t2.micro',
                KeyName=self.key_name,
                SecurityGroupIds=[self.nat_sg_id],
                SubnetId=self.public_subnet_id,
                TagSpecifications=[
                    {
                        'ResourceType': 'instance',
                        'Tags': [
                            {'Key': 'Name', 'Value': 'nat'},
                            {'Key': 'Environment', 'Value': 'Lab'}
                        ]
                    }
                ]
            )
            
            self.nat_instance_id = instance_response['Instances'][0]['InstanceId']
            logger.info(f"NAT instance launched: {self.nat_instance_id}")
            self.print_status(f"NAT instance created: {self.nat_instance_id}", "SUCCESS")
            
            # Wait for instance to be running
            if self.wait_for_instance_running(self.nat_instance_id):
                # Disable source/destination check
                self.ec2_client.modify_instance_attribute(
                    InstanceId=self.nat_instance_id,
                    SourceDestCheck={'Value': False}
                )
                logger.info(f"Source/destination check disabled for NAT instance {self.nat_instance_id}")
                self.print_status("NAT instance source/destination check disabled", "SUCCESS")
                
                # Add NAT route to private route table
                self.ec2_client.create_route(
                    RouteTableId=self.private_route_table_id,
                    DestinationCidrBlock='0.0.0.0/0',
                    InstanceId=self.nat_instance_id
                )
                logger.info(f"NAT route added to private route table {self.private_route_table_id}")
                self.print_status("NAT route added to private route table", "SUCCESS")
                return True
            else:
                return False
                
        except ClientError as e:
            error_msg = f"Error creating NAT instance: {e}"
            logger.error(error_msg)
            self.print_status(error_msg, "ERROR")
            return False
    
    def create_private_instance(self):
        """Create private instance"""
        try:
            self.print_status("Creating private instance...")
            logger.info("Starting private instance creation")
            
            # Get latest Amazon Linux 2 AMI
            response = self.ec2_client.describe_images(
                Owners=['amazon'],
                Filters=[
                    {'Name': 'name', 'Values': ['amzn2-ami-hvm-*-x86_64-gp2']},
                    {'Name': 'state', 'Values': ['available']}
                ]
            )
            ami_id = response['Images'][0]['ImageId']
            logger.info(f"Using AMI for private instance: {ami_id}")
            
            # Launch private instance
            instance_response = self.ec2_client.run_instances(
                ImageId=ami_id,
                MinCount=1,
                MaxCount=1,
                InstanceType='t2.micro',
                KeyName=self.key_name,
                SecurityGroupIds=[self.private_sg_id],
                SubnetId=self.private_subnet_id,
                TagSpecifications=[
                    {
                        'ResourceType': 'instance',
                        'Tags': [
                            {'Key': 'Name', 'Value': 'private'},
                            {'Key': 'Environment', 'Value': 'Lab'}
                        ]
                    }
                ]
            )
            
            self.private_instance_id = instance_response['Instances'][0]['InstanceId']
            logger.info(f"Private instance launched: {self.private_instance_id}")
            self.print_status(f"Private instance created: {self.private_instance_id}", "SUCCESS")
            
            # Wait for instance to be running
            if self.wait_for_instance_running(self.private_instance_id):
                self.print_status("Private instance is running", "SUCCESS")
                return True
            else:
                return False
                
        except ClientError as e:
            error_msg = f"Error creating private instance: {e}"
            logger.error(error_msg)
            self.print_status(error_msg, "ERROR")
            return False
    
    def create_ssm_role(self):
        """Create IAM role for SSM Session Manager"""
        try:
            self.print_status("Creating SSM role...")
            logger.info("Starting SSM role creation")
            
            # Create role
            role_name = 'basic-ssm'
            trust_policy = {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {"Service": "ec2.amazonaws.com"},
                        "Action": "sts:AssumeRole"
                    }
                ]
            }
            
            try:
                role_response = self.iam_client.create_role(
                    RoleName=role_name,
                    AssumeRolePolicyDocument=json.dumps(trust_policy),
                    Description='Role for SSM Session Manager access'
                )
                logger.info(f"SSM role created: {role_name}")
                self.print_status(f"SSM role created: {role_name}", "SUCCESS")
            except ClientError as e:
                if e.response['Error']['Code'] == 'EntityAlreadyExists':
                    logger.info(f"SSM role {role_name} already exists")
                    self.print_status(f"SSM role {role_name} already exists", "SUCCESS")
                else:
                    raise
            
            # Attach SSM policy
            try:
                self.iam_client.attach_role_policy(
                    RoleName=role_name,
                    PolicyArn='arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore'
                )
                logger.info("SSM policy attached to role")
                self.print_status("SSM policy attached to role", "SUCCESS")
            except ClientError as e:
                if e.response['Error']['Code'] != 'EntityAlreadyExists':
                    raise
            
            # Create instance profile
            try:
                self.iam_client.create_instance_profile(
                    InstanceProfileName=role_name
                )
                self.iam_client.add_role_to_instance_profile(
                    InstanceProfileName=role_name,
                    RoleName=role_name
                )
                logger.info("Instance profile created")
                self.print_status("Instance profile created", "SUCCESS")
            except ClientError as e:
                if e.response['Error']['Code'] != 'EntityAlreadyExists':
                    raise
            
            return True
            
        except ClientError as e:
            error_msg = f"Error creating SSM role: {e}"
            logger.error(error_msg)
            self.print_status(error_msg, "ERROR")
            return False
    
    def attach_ssm_role_to_private_instance(self):
        """Attach SSM role to private instance"""
        try:
            self.print_status("Attaching SSM role to private instance...")
            logger.info("Starting SSM role attachment to private instance")
            
            # Stop instance
            self.ec2_client.stop_instances(InstanceIds=[self.private_instance_id])
            logger.info(f"Stopping private instance {self.private_instance_id}")
            
            # Wait for instance to stop
            waiter = self.ec2_client.get_waiter('instance_stopped')
            waiter.wait(InstanceIds=[self.private_instance_id])
            logger.info(f"Private instance {self.private_instance_id} stopped")
            
            # Attach IAM role
            self.ec2_client.modify_instance_attribute(
                InstanceId=self.private_instance_id,
                IamInstanceProfile={'Name': 'basic-ssm'}
            )
            logger.info(f"IAM role attached to private instance {self.private_instance_id}")
            
            # Start instance
            self.ec2_client.start_instances(InstanceIds=[self.private_instance_id])
            logger.info(f"Starting private instance {self.private_instance_id}")
            
            # Wait for instance to start
            if self.wait_for_instance_running(self.private_instance_id):
                self.print_status("SSM role attached to private instance", "SUCCESS")
                return True
            else:
                return False
                
        except ClientError as e:
            error_msg = f"Error attaching SSM role: {e}"
            logger.error(error_msg)
            self.print_status(error_msg, "ERROR")
            return False
    
    def get_instance_info(self):
        """Get and display instance information"""
        try:
            self.print_status("Gathering instance information...")
            logger.info("Gathering instance information for display")
            
            instances = [self.bastion_instance_id, self.nat_instance_id, self.private_instance_id]
            response = self.ec2_client.describe_instances(InstanceIds=instances)
            
            print(f"\n{Fore.CYAN}📋 Instance Information:{Style.RESET_ALL}")
            print("=" * 80)
            
            for reservation in response['Reservations']:
                for instance in reservation['Instances']:
                    name = "Unknown"
                    for tag in instance.get('Tags', []):
                        if tag['Key'] == 'Name':
                            name = tag['Value']
                            break
                    
                    print(f"\n{Fore.YELLOW}Instance: {name}{Style.RESET_ALL}")
                    print(f"  Instance ID: {instance['InstanceId']}")
                    print(f"  State: {instance['State']['Name']}")
                    print(f"  Type: {instance['InstanceType']}")
                    print(f"  Public IP: {instance.get('PublicIpAddress', 'N/A')}")
                    print(f"  Private IP: {instance.get('PrivateIpAddress', 'N/A')}")
                    print(f"  Subnet: {instance['SubnetId']}")
                    
                    # Log instance details
                    logger.info(f"Instance {name}: ID={instance['InstanceId']}, State={instance['State']['Name']}, PublicIP={instance.get('PublicIpAddress', 'N/A')}, PrivateIP={instance.get('PrivateIpAddress', 'N/A')}")
                    
                    if name == 'bastion':
                        print(f"  SSH Command: ssh -i {self.key_name}.pem ec2-user@{instance.get('PublicIpAddress', 'N/A')}")
                    elif name == 'private':
                        print(f"  SSH via Bastion: ssh -i {self.key_name}.pem ec2-user@{instance.get('PrivateIpAddress', 'N/A')}")
                        print(f"  SSM Session Manager: Available through AWS Console")
            
            print(f"\n{Fore.GREEN}✅ VPC Lab setup completed successfully!{Style.RESET_ALL}")
            print(f"\n{Fore.CYAN}Next Steps:{Style.RESET_ALL}")
            print("1. Connect to bastion host using the SSH command above")
            print("2. Copy your private key to the bastion host")
            print("3. SSH to private instance through bastion")
            print("4. Or use AWS Systems Manager Session Manager for direct access")
            
            logger.info("VPC Lab setup completed successfully")
            
        except ClientError as e:
            error_msg = f"Error getting instance info: {e}"
            logger.error(error_msg)
            self.print_status(error_msg, "ERROR")
    
    def cleanup_resources(self):
        """Clean up all created resources"""
        try:
            self.print_status("Cleaning up resources...")
            logger.info("Starting resource cleanup process")
            
            # Terminate instances
            if self.private_instance_id:
                self.ec2_client.terminate_instances(InstanceIds=[self.private_instance_id])
                logger.info(f"Terminating private instance: {self.private_instance_id}")
            if self.nat_instance_id:
                self.ec2_client.terminate_instances(InstanceIds=[self.nat_instance_id])
                logger.info(f"Terminating NAT instance: {self.nat_instance_id}")
            if self.bastion_instance_id:
                self.ec2_client.terminate_instances(InstanceIds=[self.bastion_instance_id])
                logger.info(f"Terminating bastion instance: {self.bastion_instance_id}")
            
            # Wait for instances to terminate
            time.sleep(30)
            logger.info("Waited 30 seconds for instances to terminate")
            
            # Delete security groups
            for sg_id in [self.private_sg_id, self.nat_sg_id, self.bastion_sg_id]:
                if sg_id:
                    try:
                        self.ec2_client.delete_security_group(GroupId=sg_id)
                        logger.info(f"Security group deleted: {sg_id}")
                    except ClientError:
                        logger.warning(f"Could not delete security group: {sg_id}")
                        pass
            
            # Delete subnets
            for subnet_id in [self.private_subnet_id, self.public_subnet_id]:
                if subnet_id:
                    try:
                        self.ec2_client.delete_subnet(SubnetId=subnet_id)
                        logger.info(f"Subnet deleted: {subnet_id}")
                    except ClientError:
                        logger.warning(f"Could not delete subnet: {subnet_id}")
                        pass
            
            # Delete route tables
            for rt_id in [self.private_route_table_id, self.public_route_table_id]:
                if rt_id:
                    try:
                        self.ec2_client.delete_route_table(RouteTableId=rt_id)
                        logger.info(f"Route table deleted: {rt_id}")
                    except ClientError:
                        logger.warning(f"Could not delete route table: {rt_id}")
                        pass
            
            # Detach and delete internet gateway
            if self.internet_gateway_id and self.vpc_id:
                try:
                    self.ec2_client.detach_internet_gateway(
                        InternetGatewayId=self.internet_gateway_id,
                        VpcId=self.vpc_id
                    )
                    self.ec2_client.delete_internet_gateway(InternetGatewayId=self.internet_gateway_id)
                    logger.info(f"Internet gateway deleted: {self.internet_gateway_id}")
                except ClientError:
                    logger.warning(f"Could not delete internet gateway: {self.internet_gateway_id}")
                    pass
            
            # Delete VPC
            if self.vpc_id:
                try:
                    self.ec2_client.delete_vpc(VpcId=self.vpc_id)
                    logger.info(f"VPC deleted: {self.vpc_id}")
                except ClientError:
                    logger.warning(f"Could not delete VPC: {self.vpc_id}")
                    pass
            
            self.print_status("Resources cleaned up", "SUCCESS")
            logger.info("Resource cleanup completed")
            
        except ClientError as e:
            error_msg = f"Error during cleanup: {e}"
            logger.error(error_msg)
            self.print_status(error_msg, "ERROR")
    
    def run_complete_setup(self):
        """Run the complete VPC lab setup"""
        try:
            self.print_status("Starting VPC Security Architecture Lab setup...", "SUCCESS")
            logger.info("=== Starting VPC Security Architecture Lab Setup ===")
            logger.info(f"Setup started at: {datetime.now().isoformat()}")
            
            # Step 1: Create VPC and Internet Gateway
            logger.info("Step 1: Creating VPC and Internet Gateway")
            if not self.create_vpc():
                logger.error("VPC creation failed")
                return False
            
            # Step 2: Create subnets
            logger.info("Step 2: Creating subnets")
            if not self.create_subnets():
                logger.error("Subnet creation failed")
                return False
            
            # Step 3: Create route tables
            logger.info("Step 3: Creating route tables")
            if not self.create_route_tables():
                logger.error("Route table creation failed")
                return False
            
            # Step 4: Create security groups
            logger.info("Step 4: Creating security groups")
            if not self.create_security_groups():
                logger.error("Security group creation failed")
                return False
            
            # Step 5: Create key pair
            logger.info("Step 5: Creating key pair")
            if not self.create_key_pair():
                logger.error("Key pair creation failed")
                return False
            
            # Step 6: Create bastion instance
            logger.info("Step 6: Creating bastion instance")
            if not self.create_bastion_instance():
                logger.error("Bastion instance creation failed")
                return False
            
            # Step 7: Create NAT instance
            logger.info("Step 7: Creating NAT instance")
            if not self.create_nat_instance():
                logger.error("NAT instance creation failed")
                return False
            
            # Step 8: Create private instance
            logger.info("Step 8: Creating private instance")
            if not self.create_private_instance():
                logger.error("Private instance creation failed")
                return False
            
            # Step 9: Create SSM role
            logger.info("Step 9: Creating SSM role")
            if not self.create_ssm_role():
                logger.error("SSM role creation failed")
                return False
            
            # Step 10: Attach SSM role to private instance
            logger.info("Step 10: Attaching SSM role to private instance")
            if not self.attach_ssm_role_to_private_instance():
                logger.error("SSM role attachment failed")
                return False
            
            # Step 11: Display results
            logger.info("Step 11: Gathering and displaying results")
            self.get_instance_info()
            
            logger.info("=== VPC Security Architecture Lab Setup Completed Successfully ===")
            logger.info(f"Setup completed at: {datetime.now().isoformat()}")
            
            return True
            
        except Exception as e:
            error_msg = f"Unexpected error during setup: {e}"
            logger.error(error_msg)
            self.print_status(error_msg, "ERROR")
            return False

def main():
    """Main function"""
    print(f"{Fore.CYAN}🚀 AWS VPC Security Architecture Lab Automation{Style.RESET_ALL}")
    print("=" * 60)
    
    logger.info("=== VPC Automation Script Started ===")
    
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
    
    # Create VPC automation instance
    vpc_automation = VPCAutomation()
    
    # Run the complete setup
    success = vpc_automation.run_complete_setup()
    
    if not success:
        logger.error("Setup failed, starting cleanup")
        print(f"\n{Fore.RED}❌ Setup failed. Cleaning up resources...{Style.RESET_ALL}")
        vpc_automation.cleanup_resources()
    
    logger.info("=== VPC Automation Script Finished ===")

if __name__ == "__main__":
    main()
