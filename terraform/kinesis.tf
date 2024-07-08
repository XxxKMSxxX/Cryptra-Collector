variable "stream_name" {
  description = "The name of the Kinesis stream"
  type        = string
}

variable "shard_count" {
  description = "The number of shards for the Kinesis stream"
  type        = number
}

variable "retention_period" {
  description = "The retention period for the Kinesis stream in hours"
  type        = number
}

resource "aws_kinesis_stream" "this" {
  provider        = aws
  name            = var.stream_name
  shard_count     = var.shard_count
  retention_period = var.retention_period

  tags = {
    Environment = "production"
  }
}

output "stream_name" {
  value = aws_kinesis_stream.this.name
}
