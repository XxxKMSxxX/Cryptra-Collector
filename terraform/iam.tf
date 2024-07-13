# EKSクラスター用IAMロール
resource "aws_iam_role" "eks_cluster_role" {
  name = "${local.project_name}-eks-cluster-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "eks.amazonaws.com"
        }
      }
    ]
  })
}

# ECRポリシー
resource "aws_iam_policy" "ecr_policy" {
  name        = "${local.project_name}-ecr-policy"
  description = "Policy for creating and managing ECR repositories"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "ecr:CreateRepository",
          "ecr:DeleteRepository",
          "ecr:DescribeRepositories",
          "ecr:ListImages",
          "ecr:BatchCheckLayerAvailability",
          "ecr:PutImage",
          "ecr:InitiateLayerUpload",
          "ecr:UploadLayerPart",
          "ecr:CompleteLayerUpload",
          "ecr:BatchDeleteImage"
        ],
        Effect   = "Allow",
        Resource = "*"
      }
    ]
  })
}

# ECRポリシーをEKSクラスターIAMロールにアタッチ
resource "aws_iam_role_policy_attachment" "ecr_policy_attachment" {
  role       = aws_iam_role.eks_cluster_role.name
  policy_arn = aws_iam_policy.ecr_policy.arn
}
