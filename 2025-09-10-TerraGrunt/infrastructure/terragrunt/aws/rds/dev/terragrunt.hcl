include "root" {
  path = find_in_parent_folders()
}

dependency "vpc" {
  config_path = "../../vpc/dev"
}

terraform {
  source = "../../../../modules/rds"
}

inputs = {
  environment          = "dev"
  db_name              = "myappdb_dev"
  db_username          = "admin"
  db_password          = "your-secure-password"
  vpc_security_group_ids = [dependency.vpc.outputs.security_group_id]
  db_subnet_group_name  = dependency.vpc.outputs.db_subnet_group_name
}