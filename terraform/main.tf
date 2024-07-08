provider "aws" {
  region = var.aws_region
}

module "iam" {
  source = "./iam"
}

module "ecs" {
  source  = "./ecs"
  for_each = local.ecs_services

  ecs_cluster_id = module.ecs_cluster.ecs_cluster_id
  service_name   = each.key
  container_name = "collector"
  container_port = 80
  docker_image   = var.docker_image
  exchange       = each.value.exchange
  contract       = each.value.contract
  symbol         = each.value.symbol
  aws_region     = lookup(local.exchange_to_region, each.value.exchange, "us-east-1")
}

module "kinesis" {
  source  = "./kinesis"
  for_each = local.kinesis_streams

  stream_name      = each.key
  shard_count      = each.value.shard_count
  retention_period = each.value.retention_period
}

module "ecr" {
  source = "./ecr"
}
