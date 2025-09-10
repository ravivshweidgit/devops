terraform {
  backend "local" {}
}

resource "aws_db_instance" "rds_instance" {
  identifier           = "${var.project}-${var.environment}-db"
  engine               = "mysql"  # Free tier eligible
  engine_version       = "8.0.42"  # Updated to latest supported version
  instance_class      = "db.t3.micro"  # Free tier eligible
  allocated_storage   = 20  # Free tier eligible (up to 20GB)
  storage_type        = "gp2"
  
  db_name             = var.db_name
  username            = var.db_username
  password            = var.db_password
  
  skip_final_snapshot = true  # For development purposes
  
  tags = {
    Environment = var.environment
    Project     = var.project
  }
  
  vpc_security_group_ids = var.vpc_security_group_ids
  db_subnet_group_name  = var.db_subnet_group_name
}

