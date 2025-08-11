#!/usr/bin/env python3
"""
Configuration file for AWS VPC Security Architecture Lab Automation
This file contains all configurable parameters for the VPC setup
"""

# AWS Configuration
AWS_REGION = 'eu-north-1'

# VPC Configuration
VPC_CONFIG = {
    'name': 'lab-vpc',
    'cidr_block': '10.0.0.0/16',
    'enable_dns_hostnames': True,
    'enable_dns_support': True
}

# Subnet Configuration
SUBNET_CONFIG = {
    'public': {
        'name': 'lab-vpc-public',
        'cidr_block': '10.0.1.0/24',
        'map_public_ip_on_launch': True
    },
    'private': {
        'name': 'lab-vpc-private',
        'cidr_block': '10.0.2.0/24',
        'map_public_ip_on_launch': False
    }
}

# Route Table Configuration
ROUTE_TABLE_CONFIG = {
    'public': {
        'name': 'lab-vpc-public-rt'
    },
    'private': {
        'name': 'lab-vpc-private-rt'
    }
}

# Security Group Configuration
SECURITY_GROUP_CONFIG = {
    'bastion': {
        'name': 'lab-vpc-bastion-sg',
        'description': 'Security group for bastion host',
        'ingress_rules': [
            {
                'ip_protocol': 'tcp',
                'from_port': 22,
                'to_port': 22,
                'ip_ranges': [{'cidr_ip': '0.0.0.0/0'}]
            }
        ]
    },
    'nat': {
        'name': 'lab-vpc-nat-sg',
        'description': 'Security group for NAT instance',
        'ingress_rules': [
            {
                'ip_protocol': '-1',
                'ip_ranges': [{'cidr_ip': '10.0.0.0/16'}]
            }
        ]
    },
    'private': {
        'name': 'lab-vpc-private-sg',
        'description': 'Security group for private instances',
        'ingress_rules': [
            {
                'ip_protocol': 'tcp',
                'from_port': 22,
                'to_port': 22,
                'user_id_group_pairs': [{'group_id': 'bastion_sg_id'}]  # Will be replaced dynamically
            }
        ]
    }
}

# Key Pair Configuration
KEY_PAIR_CONFIG = {
    'name': 'key01',
    'key_file': 'key01.pem',
    'permissions': 0o400
}

# Instance Configuration
INSTANCE_CONFIG = {
    'bastion': {
        'name': 'bastion',
        'instance_type': 't2.micro',
        'ami_filters': [
            {'Name': 'name', 'Values': ['amzn2-ami-hvm-*-x86_64-gp2']},
            {'Name': 'state', 'Values': ['available']}
        ],
        'ami_owners': ['amazon']
    },
    'nat': {
        'name': 'nat',
        'instance_type': 't2.micro',
        'ami_filters': [
            {'Name': 'name', 'Values': ['*nat*']},
            {'Name': 'state', 'Values': ['available']}
        ],
        'ami_owners': ['amazon'],
        'fallback_ami_filters': [
            {'Name': 'name', 'Values': ['amzn2-ami-hvm-*-x86_64-gp2']},
            {'Name': 'state', 'Values': ['available']}
        ]
    },
    'private': {
        'name': 'private',
        'instance_type': 't2.micro',
        'ami_filters': [
            {'Name': 'name', 'Values': ['amzn2-ami-hvm-*-x86_64-gp2']},
            {'Name': 'state', 'Values': ['available']}
        ],
        'ami_owners': ['amazon']
    }
}

# IAM Configuration
IAM_CONFIG = {
    'role_name': 'basic-ssm',
    'instance_profile_name': 'basic-ssm',
    'trust_policy': {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {"Service": "ec2.amazonaws.com"},
                "Action": "sts:AssumeRole"
            }
        ]
    },
    'policies': [
        'arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore'
    ]
}

# Tags Configuration
TAGS_CONFIG = {
    'environment': 'Lab',
    'project': 'VPC-Security-Lab',
    'managed_by': 'boto3-automation'
}

# Timeout Configuration
TIMEOUT_CONFIG = {
    'instance_running': 300,  # 5 minutes
    'instance_stopped': 120,  # 2 minutes
    'waiter_delay': 10,
    'waiter_max_attempts': 30
}

# Logging Configuration
LOGGING_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(levelname)s - %(message)s'
}

# Color Configuration for Output
COLOR_CONFIG = {
    'success': 'GREEN',
    'error': 'RED',
    'warning': 'YELLOW',
    'info': 'BLUE',
    'header': 'CYAN'
}

# Resource Naming Patterns
NAMING_PATTERNS = {
    'vpc': '{name}',
    'subnet': '{vpc_name}-{subnet_type}',
    'route_table': '{vpc_name}-{route_type}-rt',
    'security_group': '{vpc_name}-{sg_type}-sg',
    'internet_gateway': '{vpc_name}-igw',
    'instance': '{instance_type}'
}

# Validation Rules
VALIDATION_RULES = {
    'cidr_blocks': {
        'vpc': ['10.0.0.0/8', '172.16.0.0/12', '192.168.0.0/16'],
        'subnet': ['/24', '/25', '/26', '/27', '/28']
    },
    'instance_types': [
        't2.micro', 't2.small', 't2.medium',
        't3.micro', 't3.small', 't3.medium'
    ],
    'regions': [
        'us-east-1', 'us-west-2', 'eu-west-1', 'eu-north-1',
        'ap-southeast-1', 'ap-northeast-1'
    ]
}

# Cost Optimization
COST_OPTIMIZATION = {
    'use_free_tier': True,
    'free_tier_instance_types': ['t2.micro', 't3.micro'],
    'auto_cleanup_after_hours': 24,
    'cost_alerts': {
        'enabled': False,
        'threshold_usd': 10.0
    }
}

# Security Hardening
SECURITY_HARDENING = {
    'restrict_ssh_source': False,  # Set to True to restrict SSH to specific IPs
    'allowed_ssh_ips': [],  # List of allowed IPs for SSH access
    'enable_vpc_flow_logs': False,
    'enable_cloudtrail': False,
    'encrypt_ebs_volumes': True,
    'use_imdsv2': True
}

# Monitoring and Logging
MONITORING_CONFIG = {
    'enable_cloudwatch_logs': False,
    'enable_cloudwatch_metrics': False,
    'log_retention_days': 7,
    'alarm_config': {
        'cpu_utilization_threshold': 80,
        'memory_utilization_threshold': 80,
        'disk_utilization_threshold': 80
    }
}

# Backup and Recovery
BACKUP_CONFIG = {
    'enable_automated_backups': False,
    'backup_retention_days': 7,
    'backup_schedule': 'cron(0 2 * * ? *)'  # Daily at 2 AM UTC
}

# Network Configuration
NETWORK_CONFIG = {
    'enable_nat_gateway': False,  # Use NAT Gateway instead of NAT Instance (more expensive)
    'enable_vpc_endpoints': False,
    'enable_dns_resolution': True,
    'enable_dns_hostnames': True,
    'enable_auto_assign_public_ip': True
}

# Development and Testing
DEV_CONFIG = {
    'dry_run': False,  # Set to True to simulate operations without creating resources
    'verbose_output': True,
    'save_state': True,  # Save resource IDs to file for later reference
    'state_file': 'vpc_state.json'
}
