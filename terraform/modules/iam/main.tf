resource "aws_iam_role" "github_actions_role" {
  name = "github-actions-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action = "sts:AssumeRole",
        Effect = "Allow",
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      },
    ],
  })
}

resource "aws_iam_policy" "ecr_policy" {
  name        = "github-actions-ecr-policy"
  description = "IAM policy for GitHub Actions to access ECR"

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action = [
          "ecr:*"
        ],
        Effect   = "Allow",
        Resource = "*"
      }
    ],
  })
}

resource "aws_iam_role_policy_attachment" "ecr_policy_attachment" {
  role       = aws_iam_role.github_actions_role.name
  policy_arn = aws_iam_policy.ecr_policy.arn
}
