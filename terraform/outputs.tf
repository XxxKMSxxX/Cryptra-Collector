output "ecr_repository_url" {
  value = aws_ecr_repository.my_repository.repository_url
}

output "eks_cluster_role_arn" {
  value = aws_iam_role.eks_cluster_role.arn
}

output "ecr_policy_arn" {
  value = aws_iam_policy.ecr_policy.arn
}

output "eks_cluster_name" {
  value = aws_eks_cluster.my_cluster.name
}

output "kinesis_stream_name" {
  value = aws_kinesis_stream.my_stream.name
}
