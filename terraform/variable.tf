variable "exchange" {
  description = "Exchange name"
  type        = string
}

variable "aws_region" {
  description = "The AWS region to deploy to"
  type        = string
}

variable "docker_image" {
  description = "Docker image for the collector service"
  type        = string
  default     = "${aws_ecr_repository.collector.repository_url}:latest"
}

variable "ecs_services" {
  description = "ECS services configurations"
  type = map(object({
    exchange = string
    contract = string
    symbol   = string
  }))
}

variable "kinesis_streams" {
  description = "Kinesis streams configurations"
  type = map(object({
    shard_count     = number
    retention_period = number
  }))
}
