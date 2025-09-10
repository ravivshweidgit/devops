include "root" {
  path = find_in_parent_folders()
}

terraform {
  source = "../../../../modules/rds"
}

inputs = {
  environment  = "prod"
  db_name      = "myappdb_prod"
  db_username  = "admin"
  db_password  = "your-secure-password"
}