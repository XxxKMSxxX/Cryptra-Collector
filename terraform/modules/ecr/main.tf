variable "repository_name" {
  description = "The name of the ECR repository"
  type        = string
}

resource "aws_ecr_repository" "repository" {
  name                 = var.repository_name
  image_tag_mutability = "MUTABLE"
  image_scanning_configuration {
    scan_on_push = true
  }
}
