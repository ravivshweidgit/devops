#!/usr/bin/env python3
"""
Cleanup script for AWS VPC Security Architecture Lab
This script removes all resources created by the VPC automation
"""

import boto3
import time
from botocore.exceptions import ClientError
from colorama import init, Fore, Style
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
    logger = logging.getLogger('vpc_cleanup')
    logger.setLevel(logging.INFO)
    
    # Clear any existing handlers
    logger.handlers.clear()
    
    # Create formatters
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_formatter = logging.Formatter('%(message)s')
    
    # File handler for app.log (append mode for cleanup)
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

class VPCCleanup:
    def __init__(self, region='eu-north-1'):
        """Initialize the VPC cleanup class"""
        self.region = region
        self.ec2_client = boto3.client('ec2', region_name=region)
        self.iam_client = boto3.client('iam')
        
        # Resource names to clean up
        self.vpc_name = 'lab-vpc'
        self.key_name = 'key01'
        self.role_name = 'basic-ssm'
        
        # Log initialization
        logger.info(f"VPC Cleanup initialized for region: {region}")
        logger.info(f"Looking for resources with VPC name: {self.vpc_name}")
        
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
    
    def find_resources_by_tags(self):
        """Find resources by tags"""
        resources = {
            'instances': [],
            'security_groups': [],
            'subnets': [],
            'route_tables': [],
            'internet_gateways': [],
            'vpcs': []
        }
        
        try:
            logger.info("Starting resource discovery by tags")
            
            # Find VPCs
            vpc_response = self.ec2_client.describe_vpcs(
                Filters=[
                    {'Name': 'tag:Name', 'Values': [self.vpc_name]},
                    {'Name': 'tag:Environment', 'Values': ['Lab']}
                ]
            )
            
            for vpc in vpc_response['Vpcs']:
                resources['vpcs'].append(vpc['VpcId'])
                logger.info(f"Found VPC: {vpc['VpcId']}")
                
                # Find subnets in this VPC
                subnet_response = self.ec2_client.describe_subnets(
                    Filters=[
                        {'Name': 'vpc-id', 'Values': [vpc['VpcId']]},
                        {'Name': 'tag:Environment', 'Values': ['Lab']}
                    ]
                )
                for subnet in subnet_response['Subnets']:
                    resources['subnets'].append(subnet['SubnetId'])
                    logger.info(f"Found subnet: {subnet['SubnetId']}")
                
                # Find route tables in this VPC
                rt_response = self.ec2_client.describe_route_tables(
                    Filters=[
                        {'Name': 'vpc-id', 'Values': [vpc['VpcId']]},
                        {'Name': 'tag:Environment', 'Values': ['Lab']}
                    ]
                )
                for rt in rt_response['RouteTables']:
                    resources['route_tables'].append(rt['RouteTableId'])
                    logger.info(f"Found route table: {rt['RouteTableId']}")
                
                # Find security groups in this VPC
                sg_response = self.ec2_client.describe_security_groups(
                    Filters=[
                        {'Name': 'vpc-id', 'Values': [vpc['VpcId']]},
                        {'Name': 'tag:Environment', 'Values': ['Lab']}
                    ]
                )
                for sg in sg_response['SecurityGroups']:
                    resources['security_groups'].append(sg['GroupId'])
                    logger.info(f"Found security group: {sg['GroupId']}")
                
                # Find internet gateways attached to this VPC
                igw_response = self.ec2_client.describe_internet_gateways(
                    Filters=[
                        {'Name': 'attachment.vpc-id', 'Values': [vpc['VpcId']]},
                        {'Name': 'tag:Environment', 'Values': ['Lab']}
                    ]
                )
                for igw in igw_response['InternetGateways']:
                    resources['internet_gateways'].append(igw['InternetGatewayId'])
                    logger.info(f"Found internet gateway: {igw['InternetGatewayId']}")
            
            # Find instances by tags
            instance_response = self.ec2_client.describe_instances(
                Filters=[
                    {'Name': 'tag:Environment', 'Values': ['Lab']},
                    {'Name': 'instance-state-name', 'Values': ['pending', 'running', 'stopping', 'stopped']}
                ]
            )
            
            for reservation in instance_response['Reservations']:
                for instance in reservation['Instances']:
                    resources['instances'].append(instance['InstanceId'])
                    logger.info(f"Found instance: {instance['InstanceId']} (state: {instance['State']['Name']})")
            
            logger.info(f"Resource discovery completed. Found: {sum(len(v) for v in resources.values())} resources")
            return resources
            
        except ClientError as e:
            error_msg = f"Error finding resources: {e}"
            logger.error(error_msg)
            self.print_status(error_msg, "ERROR")
            return resources
    
    def terminate_instances(self, instance_ids):
        """Terminate EC2 instances"""
        if not instance_ids:
            return True
            
        try:
            self.print_status(f"Terminating {len(instance_ids)} instances...")
            logger.info(f"Starting termination of {len(instance_ids)} instances: {instance_ids}")
            
            # Terminate instances
            self.ec2_client.terminate_instances(InstanceIds=instance_ids)
            
            # Wait for instances to terminate
            waiter = self.ec2_client.get_waiter('instance_terminated')
            waiter.wait(InstanceIds=instance_ids, WaiterConfig={'Delay': 10, 'MaxAttempts': 30})
            
            logger.info("All instances terminated successfully")
            self.print_status("All instances terminated", "SUCCESS")
            return True
            
        except ClientError as e:
            error_msg = f"Error terminating instances: {e}"
            logger.error(error_msg)
            self.print_status(error_msg, "ERROR")
            return False
    
    def delete_security_groups(self, security_group_ids):
        """Delete security groups"""
        if not security_group_ids:
            return True
            
        try:
            self.print_status(f"Deleting {len(security_group_ids)} security groups...")
            logger.info(f"Starting deletion of {len(security_group_ids)} security groups: {security_group_ids}")
            
            for sg_id in security_group_ids:
                try:
                    self.ec2_client.delete_security_group(GroupId=sg_id)
                    logger.info(f"Security group deleted successfully: {sg_id}")
                    self.print_status(f"Security group {sg_id} deleted", "SUCCESS")
                except ClientError as e:
                    if e.response['Error']['Code'] == 'DependencyViolation':
                        warning_msg = f"Security group {sg_id} has dependencies, skipping"
                        logger.warning(warning_msg)
                        self.print_status(warning_msg, "WARNING")
                    else:
                        error_msg = f"Error deleting security group {sg_id}: {e}"
                        logger.error(error_msg)
                        self.print_status(error_msg, "ERROR")
            
            return True
            
        except ClientError as e:
            error_msg = f"Error deleting security groups: {e}"
            logger.error(error_msg)
            self.print_status(error_msg, "ERROR")
            return False
    
    def delete_subnets(self, subnet_ids):
        """Delete subnets"""
        if not subnet_ids:
            return True
            
        try:
            self.print_status(f"Deleting {len(subnet_ids)} subnets...")
            logger.info(f"Starting deletion of {len(subnet_ids)} subnets: {subnet_ids}")
            
            for subnet_id in subnet_ids:
                try:
                    self.ec2_client.delete_subnet(SubnetId=subnet_id)
                    logger.info(f"Subnet deleted successfully: {subnet_id}")
                    self.print_status(f"Subnet {subnet_id} deleted", "SUCCESS")
                except ClientError as e:
                    error_msg = f"Error deleting subnet {subnet_id}: {e}"
                    logger.error(error_msg)
                    self.print_status(error_msg, "ERROR")
            
            return True
            
        except ClientError as e:
            error_msg = f"Error deleting subnets: {e}"
            logger.error(error_msg)
            self.print_status(error_msg, "ERROR")
            return False
    
    def delete_route_tables(self, route_table_ids):
        """Delete route tables"""
        if not route_table_ids:
            return True
            
        try:
            self.print_status(f"Deleting {len(route_table_ids)} route tables...")
            logger.info(f"Starting deletion of {len(route_table_ids)} route tables: {route_table_ids}")
            
            for rt_id in route_table_ids:
                try:
                    self.ec2_client.delete_route_table(RouteTableId=rt_id)
                    logger.info(f"Route table deleted successfully: {rt_id}")
                    self.print_status(f"Route table {rt_id} deleted", "SUCCESS")
                except ClientError as e:
                    if e.response['Error']['Code'] == 'DependencyViolation':
                        warning_msg = f"Route table {rt_id} has dependencies, skipping"
                        logger.warning(warning_msg)
                        self.print_status(warning_msg, "WARNING")
                    else:
                        error_msg = f"Error deleting route table {rt_id}: {e}"
                        logger.error(error_msg)
                        self.print_status(error_msg, "ERROR")
            
            return True
            
        except ClientError as e:
            error_msg = f"Error deleting route tables: {e}"
            logger.error(error_msg)
            self.print_status(error_msg, "ERROR")
            return False
    
    def delete_internet_gateways(self, internet_gateway_ids, vpc_ids):
        """Delete internet gateways"""
        if not internet_gateway_ids or not vpc_ids:
            return True
            
        try:
            self.print_status(f"Deleting {len(internet_gateway_ids)} internet gateways...")
            logger.info(f"Starting deletion of {len(internet_gateway_ids)} internet gateways: {internet_gateway_ids}")
            
            for igw_id in internet_gateway_ids:
                try:
                    # Detach from VPC first
                    for vpc_id in vpc_ids:
                        try:
                            self.ec2_client.detach_internet_gateway(
                                InternetGatewayId=igw_id,
                                VpcId=vpc_id
                            )
                            logger.info(f"Internet gateway {igw_id} detached from VPC {vpc_id}")
                        except ClientError:
                            logger.warning(f"Could not detach internet gateway {igw_id} from VPC {vpc_id}")
                            pass
                    
                    # Delete internet gateway
                    self.ec2_client.delete_internet_gateway(InternetGatewayId=igw_id)
                    logger.info(f"Internet gateway deleted successfully: {igw_id}")
                    self.print_status(f"Internet gateway {igw_id} deleted", "SUCCESS")
                except ClientError as e:
                    error_msg = f"Error deleting internet gateway {igw_id}: {e}"
                    logger.error(error_msg)
                    self.print_status(error_msg, "ERROR")
            
            return True
            
        except ClientError as e:
            error_msg = f"Error deleting internet gateways: {e}"
            logger.error(error_msg)
            self.print_status(error_msg, "ERROR")
            return False
    
    def delete_vpcs(self, vpc_ids):
        """Delete VPCs"""
        if not vpc_ids:
            return True
            
        try:
            self.print_status(f"Deleting {len(vpc_ids)} VPCs...")
            logger.info(f"Starting deletion of {len(vpc_ids)} VPCs: {vpc_ids}")
            
            for vpc_id in vpc_ids:
                try:
                    self.ec2_client.delete_vpc(VpcId=vpc_id)
                    logger.info(f"VPC deleted successfully: {vpc_id}")
                    self.print_status(f"VPC {vpc_id} deleted", "SUCCESS")
                except ClientError as e:
                    error_msg = f"Error deleting VPC {vpc_id}: {e}"
                    logger.error(error_msg)
                    self.print_status(error_msg, "ERROR")
            
            return True
            
        except ClientError as e:
            error_msg = f"Error deleting VPCs: {e}"
            logger.error(error_msg)
            self.print_status(error_msg, "ERROR")
            return False
    
    def delete_key_pair(self):
        """Delete key pair"""
        try:
            self.print_status(f"Deleting key pair: {self.key_name}")
            logger.info(f"Starting deletion of key pair: {self.key_name}")
            
            # Check if key pair exists
            try:
                self.ec2_client.describe_key_pairs(KeyNames=[self.key_name])
            except ClientError:
                warning_msg = f"Key pair {self.key_name} not found"
                logger.warning(warning_msg)
                self.print_status(warning_msg, "WARNING")
                return True
            
            # Delete key pair
            self.ec2_client.delete_key_pair(KeyName=self.key_name)
            logger.info(f"Key pair deleted successfully: {self.key_name}")
            self.print_status(f"Key pair {self.key_name} deleted", "SUCCESS")
            
            # Remove key file if it exists
            import os
            key_file = f"{self.key_name}.pem"
            if os.path.exists(key_file):
                os.remove(key_file)
                logger.info(f"Key file removed: {key_file}")
                self.print_status(f"Key file {key_file} removed", "SUCCESS")
            
            return True
            
        except ClientError as e:
            error_msg = f"Error deleting key pair: {e}"
            logger.error(error_msg)
            self.print_status(error_msg, "ERROR")
            return False
    
    def delete_iam_role(self):
        """Delete IAM role and instance profile"""
        try:
            self.print_status(f"Deleting IAM role: {self.role_name}")
            logger.info(f"Starting deletion of IAM role: {self.role_name}")
            
            # Remove role from instance profile
            try:
                self.iam_client.remove_role_from_instance_profile(
                    InstanceProfileName=self.role_name,
                    RoleName=self.role_name
                )
                logger.info("Role removed from instance profile successfully")
                self.print_status("Role removed from instance profile", "SUCCESS")
            except ClientError:
                logger.warning("Could not remove role from instance profile")
                pass
            
            # Delete instance profile
            try:
                self.iam_client.delete_instance_profile(InstanceProfileName=self.role_name)
                logger.info("Instance profile deleted successfully")
                self.print_status("Instance profile deleted", "SUCCESS")
            except ClientError:
                logger.warning("Could not delete instance profile")
                pass
            
            # Detach policies from role
            try:
                attached_policies = self.iam_client.list_attached_role_policies(RoleName=self.role_name)
                for policy in attached_policies['AttachedPolicies']:
                    self.iam_client.detach_role_policy(
                        RoleName=self.role_name,
                        PolicyArn=policy['PolicyArn']
                    )
                logger.info("Policies detached from role successfully")
                self.print_status("Policies detached from role", "SUCCESS")
            except ClientError:
                logger.warning("Could not detach policies from role")
                pass
            
            # Delete role
            try:
                self.iam_client.delete_role(RoleName=self.role_name)
                logger.info(f"IAM role deleted successfully: {self.role_name}")
                self.print_status(f"IAM role {self.role_name} deleted", "SUCCESS")
            except ClientError as e:
                if e.response['Error']['Code'] == 'NoSuchEntity':
                    warning_msg = f"IAM role {self.role_name} not found"
                    logger.warning(warning_msg)
                    self.print_status(warning_msg, "WARNING")
                else:
                    error_msg = f"Error deleting IAM role: {e}"
                    logger.error(error_msg)
                    self.print_status(error_msg, "ERROR")
            
            return True
            
        except ClientError as e:
            error_msg = f"Error deleting IAM role: {e}"
            logger.error(error_msg)
            self.print_status(error_msg, "ERROR")
            return False
    
    def cleanup_all(self):
        """Clean up all resources"""
        try:
            self.print_status("Starting cleanup process...", "SUCCESS")
            logger.info("=== Starting VPC Cleanup Process ===")
            logger.info(f"Cleanup started at: {datetime.now().isoformat()}")
            
            # Find all resources
            resources = self.find_resources_by_tags()
            
            if not any(resources.values()):
                warning_msg = "No resources found to clean up"
                logger.warning(warning_msg)
                self.print_status(warning_msg, "WARNING")
                return True
            
            # Display found resources
            print(f"\n{Fore.CYAN}Found resources to clean up:{Style.RESET_ALL}")
            logger.info("Resources found for cleanup:")
            for resource_type, resource_list in resources.items():
                if resource_list:
                    print(f"  {resource_type}: {len(resource_list)} resources")
                    logger.info(f"  {resource_type}: {len(resource_list)} resources - {resource_list}")
            
            # Clean up in reverse order of dependencies
            success = True
            
            # 1. Terminate instances
            logger.info("Step 1: Terminating instances")
            if not self.terminate_instances(resources['instances']):
                success = False
            
            # 2. Delete security groups
            logger.info("Step 2: Deleting security groups")
            if not self.delete_security_groups(resources['security_groups']):
                success = False
            
            # 3. Delete subnets
            logger.info("Step 3: Deleting subnets")
            if not self.delete_subnets(resources['subnets']):
                success = False
            
            # 4. Delete route tables
            logger.info("Step 4: Deleting route tables")
            if not self.delete_route_tables(resources['route_tables']):
                success = False
            
            # 5. Delete internet gateways
            logger.info("Step 5: Deleting internet gateways")
            if not self.delete_internet_gateways(resources['internet_gateways'], resources['vpcs']):
                success = False
            
            # 6. Delete VPCs
            logger.info("Step 6: Deleting VPCs")
            if not self.delete_vpcs(resources['vpcs']):
                success = False
            
            # 7. Delete key pair
            logger.info("Step 7: Deleting key pair")
            if not self.delete_key_pair():
                success = False
            
            # 8. Delete IAM role
            logger.info("Step 8: Deleting IAM role")
            if not self.delete_iam_role():
                success = False
            
            if success:
                logger.info("=== VPC Cleanup Process Completed Successfully ===")
                self.print_status("Cleanup completed successfully!", "SUCCESS")
            else:
                logger.warning("=== VPC Cleanup Process Completed with Some Errors ===")
                self.print_status("Cleanup completed with some errors", "WARNING")
            
            logger.info(f"Cleanup completed at: {datetime.now().isoformat()}")
            return success
            
        except Exception as e:
            error_msg = f"Unexpected error during cleanup: {e}"
            logger.error(error_msg)
            self.print_status(error_msg, "ERROR")
            return False

def main():
    """Main function"""
    print(f"{Fore.CYAN}🧹 AWS VPC Security Architecture Lab Cleanup{Style.RESET_ALL}")
    print("=" * 60)
    
    logger.info("=== VPC Cleanup Script Started ===")
    
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
    
    # Create cleanup instance
    cleanup = VPCCleanup()
    
    # Confirm cleanup
    print(f"\n{Fore.YELLOW}⚠️  This will delete ALL resources created by the VPC automation!{Style.RESET_ALL}")
    response = input("Are you sure you want to continue? (yes/no): ")
    
    if response.lower() in ['yes', 'y']:
        logger.info("User confirmed cleanup operation")
        cleanup.cleanup_all()
    else:
        logger.info("User cancelled cleanup operation")
        print(f"{Fore.BLUE}Cleanup cancelled{Style.RESET_ALL}")
    
    logger.info("=== VPC Cleanup Script Finished ===")

if __name__ == "__main__":
    main()
