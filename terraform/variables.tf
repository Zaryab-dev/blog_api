variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Environment name"
  type        = string
}

variable "vpc_cidr" {
  description = "VPC CIDR block"
  type        = string
  default     = "10.0.0.0/16"
}

variable "rds_multi_az" {
  description = "Enable RDS multi-AZ"
  type        = bool
  default     = true
}

variable "rds_instance_class" {
  description = "RDS instance class"
  type        = string
  default     = "db.t3.medium"
}

variable "redis_node_type" {
  description = "ElastiCache node type"
  type        = string
  default     = "cache.t3.micro"
}

variable "django_image" {
  description = "Django Docker image"
  type        = string
}

variable "celery_image" {
  description = "Celery Docker image"
  type        = string
}

variable "ecs_min_capacity" {
  description = "ECS minimum task count"
  type        = number
  default     = 2
}

variable "ecs_max_capacity" {
  description = "ECS maximum task count"
  type        = number
  default     = 10
}

variable "domain_name" {
  description = "Domain name"
  type        = string
}
