
output "rds_endpoint" {
  description = "RDS instance endpoint"
  value       = aws_db_instance.rds_instance.endpoint
}

output "rds_port" {
  description = "RDS instance port"
  value       = aws_db_instance.rds_instance.port
}

output "rds_identifier" {
  description = "RDS instance identifier"
  value       = aws_db_instance.rds_instance.identifier
}

output "rds_username" {
  description = "RDS instance username"
  value       = aws_db_instance.rds_instance.username
  sensitive   = true
}

output "rds_database_name" {
  description = "RDS database name"
  value       = aws_db_instance.rds_instance.db_name
}