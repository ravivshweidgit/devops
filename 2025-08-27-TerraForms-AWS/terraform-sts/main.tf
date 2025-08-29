data "aws_caller_identity" "current" {}

output "user_info" {
  value = data.aws_caller_identity.current
}

resource "aws_s3_bucket" "example_bucket" {
  bucket = "example-bucket-${random_id.s3_id.dec}"
  tags = {
    Environment = "dev"
    Project     = "TerraformSTS"
  }
}

resource "random_id" "s3_id" {
  byte_length = 2
}