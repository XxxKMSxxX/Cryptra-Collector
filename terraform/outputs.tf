output "ecs_cluster_id" {
  value = aws_ecs_cluster.ecs_cluster.id
}

output "kinesis_stream_arns" {
  value = aws_kinesis_stream.stream[*].arn
}
