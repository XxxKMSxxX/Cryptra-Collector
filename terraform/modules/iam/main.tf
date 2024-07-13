data "aws_iam_policy" "existing_execution_policy" {
  name = "github-actions-execution-policy"
}

resource "aws_iam_policy" "execution_policy" {
  name        = "github-actions-execution-policy"
  description = "Policy to allow AWS operations for github-actions user"
  policy      = file("${path.module}/policy.json")

  count = length(data.aws_iam_policy.existing_execution_policy.arn) == 0 ? 1 : 0
}

resource "aws_iam_user_policy_attachment" "github_actions_policy_attachment" {
  user       = "github-actions"
  policy_arn = coalesce(data.aws_iam_policy.existing_execution_policy.arn, aws_iam_policy.execution_policy.arn)
}