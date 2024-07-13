resource "aws_kinesis_stream" "my_stream" {
  name        = "${local.project_name}-kinesis-stream"
  shard_count = 1
}
