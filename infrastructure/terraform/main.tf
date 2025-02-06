provider "aws" {
  region = "us-east-1"
}

resource "aws_vpc" "app_vpc" {
  cidr_block = "10.0.0.0/16"
}

resource "aws_subnet" "app_subnet" {
  vpc_id                  = aws_vpc.app_vpc.id
  cidr_block              = "10.0.1.0/24"
  map_public_ip_on_launch = true
  availability_zone       = "us-east-1a"
}

resource "aws_security_group" "app_sg" {
  vpc_id = aws_vpc.app_vpc.id

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  ingress {
    from_port   = 8000
    to_port     = 8000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  ingress {
    from_port   = 3000
    to_port     = 3000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_ecs_cluster" "app_cluster" {
  name = "app-cluster"
}

resource "aws_ecs_task_definition" "app_task" {
  family                   = "app-task"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "512"
  memory                   = "1024"

  container_definitions = jsonencode([
    {
      name      = "backend"
      image     = "your-dockerhub-username/backend:latest"
      cpu       = 256
      memory    = 512
      essential = true
      portMappings = [{ containerPort = 8000 }]
    },
    {
      name      = "frontend"
      image     = "your-dockerhub-username/frontend:latest"
      cpu       = 256
      memory    = 512
      essential = true
      portMappings = [{ containerPort = 3000 }]
    }
  ])
}

resource "aws_ecs_service" "app_service" {
  name            = "app-service"
  cluster         = aws_ecs_cluster.app_cluster.id
  task_definition = aws_ecs_task_definition.app_task.arn
  launch_type     = "FARGATE"

  network_configuration {
    subnets         = [aws_subnet.app_subnet.id]
    security_groups = [aws_security_group.app_sg.id]
    assign_public_ip = true
  }
}

resource "aws_alb" "app_alb" {
  name               = "app-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.app_sg.id]
  subnets           = [aws_subnet.app_subnet.id]
}

resource "aws_alb_target_group" "app_tg" {
  name     = "app-tg"
  port     = 80
  protocol = "HTTP"
  vpc_id   = aws_vpc.app_vpc.id
}

resource "aws_alb_listener" "app_listener" {
  load_balancer_arn = aws_alb.app_alb.arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_alb_target_group.app_tg.arn
  }
}

output "load_balancer_dns" {
  value = aws_alb.app_alb.dns_name
}

output "ecs_cluster_name" {
  value = aws_ecs_cluster.app_cluster.name
}

output "ecs_service_name" {
  value = aws_ecs_service.app_service.name
}

output "task_definition" {
  value = aws_ecs_task_definition.app_task.family
}

output "vpc_id" {
  value = aws_vpc.app_vpc.id
}

# Deployment Instructions:
# 1. Ensure Terraform is installed.
# 2. Run `terraform init` to initialize Terraform.
# 3. Run `terraform apply -auto-approve` to deploy resources.
# 4. Retrieve the Load Balancer DNS from the outputs and access the application.
# 5. Ensure the ECS Fargate service is running and pulling the latest container images.
