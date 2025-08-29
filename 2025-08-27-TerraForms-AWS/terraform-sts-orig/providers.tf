terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~>4.0"
    }
  }
}


provider "aws" {

  region = "us-east-1"
  profile = "<profile name here>"
  assume_role {
    role_arn     = "<role arn here>"
    session_name = "terraform-session"
  }
}