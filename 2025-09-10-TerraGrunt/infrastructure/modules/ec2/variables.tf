variable "environment" {
  type        = string
  description = "Environment name"
}

variable "project" {
  type        = string
  description = "Project name"
}

variable "aws_region" {
  type        = string
  description = "AWS region"
}

variable "vpc_id" {
  type        = string
  description = "VPC ID where the bastion will be deployed"
}

variable "public_subnet_id" {
  type        = string
  description = "Public subnet ID for the bastion host"
}

variable "public_key" {
  type        = string
  description = "Public key for SSH access to bastion host"
}
