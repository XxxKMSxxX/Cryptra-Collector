resource "aws_iam_policy" "ecr_policy" {
  name        = "github-actions-ecr-policy"
  description = "Policy to allow ECR operations for github-actions user"

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action = [
          "ecr:CreateRepository",
        ],
        Effect: "Allow",
        Resource: "*"
      }
    ],
  })
}

resource "aws_iam_user_policy_attachment" "github_actions_policy_attachment" {
  user       = "github-actions"
  policy_arn = aws_iam_policy.ecr_policy.arn
}
