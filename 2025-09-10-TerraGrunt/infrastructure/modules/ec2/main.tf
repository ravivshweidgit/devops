terraform {
  backend "local" {}
}

# Security group for bastion host
resource "aws_security_group" "bastion" {
  name        = "${var.project}-${var.environment}-bastion"
  description = "Security group for bastion host"
  vpc_id      = var.vpc_id

  # SSH access from anywhere (for bastion)
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # All outbound traffic
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name        = "${var.project}-${var.environment}-bastion-sg"
    Environment = var.environment
    Project     = var.project
  }
}

# Key pair for SSH access
resource "aws_key_pair" "bastion" {
  key_name   = "${var.project}-${var.environment}-bastion-key"
  public_key = var.public_key

  tags = {
    Environment = var.environment
    Project     = var.project
  }
}

# Bastion host EC2 instance
resource "aws_instance" "bastion" {
  ami                    = data.aws_ami.amazon_linux.id
  instance_type          = "t2.micro"  # Free tier eligible
  key_name              = aws_key_pair.bastion.key_name
  vpc_security_group_ids = [aws_security_group.bastion.id]
  subnet_id             = var.public_subnet_id

  user_data = <<-EOF
    #!/bin/bash
    yum update -y
    yum install -y mysql
  EOF

  tags = {
    Name        = "${var.project}-${var.environment}-bastion"
    Environment = var.environment
    Project     = var.project
  }
}

# Get latest Amazon Linux 2 AMI
data "aws_ami" "amazon_linux" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["amzn2-ami-hvm-*-x86_64-gp2"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}
