resource "aws_ecs_cluster" "ecs_cluster" {
  name = "collector-cluster"
}

resource "aws_ecs_task_definition" "collector" {
  family                   = "collector-task"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  execution_role_arn       = module.iam.ecs_task_execution_role_arn
  task_role_arn            = module.iam.ecs_task_execution_role_arn
  cpu                      = "256"
  memory                   = "512"

  container_definitions = jsonencode([
    {
      name      = var.container_name
      image     = "${aws_ecr_repository.collector.repository_url}:latest"
      essential = true
      portMappings = [
        {
          containerPort = var.container_port
          hostPort      = var.container_port
        }
      ]
      environment = [
        {
          name  = "EXCHANGE"
          value = var.exchange
        },
        {
          name  = "CONTRACT"
          value = var.contract
        },
        {
          name  = "SYMBOL"
          value = var.symbol
        },
        {
          name  = "AWS_REGION"
          value = var.aws_region
        }
      ]
    }
  ])
}

resource "aws_ecs_service" "collector" {
  name            = var.service_name
  cluster         = var.ecs_cluster_id
  task_definition = aws_ecs_task_definition.collector.arn
  desired_count   = 1
  launch_type     = "FARGATE"
  network_configuration {
    subnets         = var.subnets
    security_groups = [var.security_group_id]
  }
}
