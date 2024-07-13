resource "aws_ecr_repository" "collector" {
  name = "${local.project_name}-ecr-repo"
}
