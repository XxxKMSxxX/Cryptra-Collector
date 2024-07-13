resource "aws_iam_policy" "execution_policy" {
  name        = "github-actions-execution-policy"
  description = "Policy to allow AWS operations for github-actions user"
  policy      = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Sid = "ECRPermissions",
        Effect = "Allow",
        Action = [
          "ecr:CreateRepository",
          "ecr:DeleteRepository",
          "ecr:DescribeRepositories",
          "ecr:ListTagsForResource",
          "ecr:PutImageScanningConfiguration",
          "ecr:CompleteLayerUpload",
          "ecr:UploadLayerPart",
          "ecr:InitiateLayerUpload",
          "ecr:BatchCheckLayerAvailability",
          "ecr:BatchDeleteImage",
          "ecr:BatchGetImage",
          "ecr:GetDownloadUrlForLayer",
          "ecr:GetRepositoryPolicy",
          "ecr:ListImages",
          "ecr:PutImage",
          "ecr:PutLifecyclePolicy",
          "ecr:GetLifecyclePolicy",
          "ecr:DeleteLifecyclePolicy"
        ],
        Resource = "*"
      },
      {
        Sid = "ECRPublicPermissions",
        Effect = "Allow",
        Action = [
          "ecr-public:CreateRepository",
          "ecr-public:DeleteRepository",
          "ecr-public:DescribeRepositories",
          "ecr-public:ListTagsForResource",
          "ecr-public:PutImageScanningConfiguration",
          "ecr-public:CompleteLayerUpload",
          "ecr-public:UploadLayerPart",
          "ecr-public:InitiateLayerUpload",
          "ecr-public:BatchCheckLayerAvailability",
          "ecr-public:BatchDeleteImage",
          "ecr-public:BatchGetImage",
          "ecr-public:GetDownloadUrlForLayer",
          "ecr-public:GetRepositoryPolicy",
          "ecr-public:ListImages",
          "ecr-public:PutImage",
          "ecr-public:PutLifecyclePolicy",
          "ecr-public:GetLifecyclePolicy",
          "ecr-public:DeleteLifecyclePolicy"
        ],
        Resource = "*"
      }
    ]
  })
}

resource "aws_iam_user_policy_attachment" "github_actions_policy_attachment" {
  user       = "github-actions"
  policy_arn = aws_iam_policy.execution_policy.arn
}
