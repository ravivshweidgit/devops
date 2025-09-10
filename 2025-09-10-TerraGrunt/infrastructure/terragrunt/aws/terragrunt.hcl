# Root terragrunt.hcl
# Option 1: Use local backend initially (comment out remote_state block)
# remote_state {
#   backend = "s3"
#   config = {
#     bucket         = "ravivsh-us-east-kuku-riku"  # Change this to a unique name
#     key            = "${path_relative_to_include()}/terraform.tfstate"
#     region         = "us-east-1"  # Free tier is available in us-east-1
#     encrypt        = true
#     dynamodb_table = "terraform-locks"
#   }
# }

# Option 2: Use local backend for now
remote_state {
  backend = "local"
  config = {
    path = "${path_relative_to_include()}/terraform.tfstate"
  }
}

inputs = {
  aws_region = "us-east-1"
  project    = "raviv-project"
}