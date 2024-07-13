output "execution_policy_arn" {
  value = coalesce(
    length(data.aws_iam_policy.existing_execution_policy.arn) == 0 ? null : data.aws_iam_policy.existing_execution_policy.arn,
    aws_iam_policy.execution_policy[0].arn
  )
}
