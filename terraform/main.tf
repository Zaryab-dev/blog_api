terraform {
  required_version = ">= 1.0"
  
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  
  backend "s3" {
    bucket = "leather-api-terraform-state"
    key    = "production/terraform.tfstate"
    region = "us-east-1"
  }
}

provider "aws" {
  region = var.aws_region
}

# VPC Module
module "vpc" {
  source = "./modules/vpc"
  
  environment = var.environment
  vpc_cidr    = var.vpc_cidr
}

# RDS Module
module "rds" {
  source = "./modules/rds"
  
  environment         = var.environment
  vpc_id              = module.vpc.vpc_id
  private_subnet_ids  = module.vpc.private_subnet_ids
  multi_az            = var.rds_multi_az
  instance_class      = var.rds_instance_class
}

# ElastiCache Module
module "elasticache" {
  source = "./modules/elasticache"
  
  environment        = var.environment
  vpc_id             = module.vpc.vpc_id
  private_subnet_ids = module.vpc.private_subnet_ids
  node_type          = var.redis_node_type
}

# S3 Module
module "s3" {
  source = "./modules/s3"
  
  environment = var.environment
}

# ECS Module
module "ecs" {
  source = "./modules/ecs"
  
  environment        = var.environment
  vpc_id             = module.vpc.vpc_id
  public_subnet_ids  = module.vpc.public_subnet_ids
  private_subnet_ids = module.vpc.private_subnet_ids
  
  db_host            = module.rds.endpoint
  redis_host         = module.elasticache.endpoint
  s3_bucket          = module.s3.media_bucket_name
  
  django_image       = var.django_image
  celery_image       = var.celery_image
  
  min_capacity       = var.ecs_min_capacity
  max_capacity       = var.ecs_max_capacity
}

# CloudFront Module
module "cloudfront" {
  source = "./modules/cloudfront"
  
  environment     = var.environment
  s3_bucket_name  = module.s3.media_bucket_name
  alb_dns_name    = module.ecs.alb_dns_name
  domain_name     = var.domain_name
}

# Route53 Module
module "route53" {
  source = "./modules/route53"
  
  domain_name           = var.domain_name
  cloudfront_domain     = module.cloudfront.domain_name
  cloudfront_zone_id    = module.cloudfront.zone_id
  alb_dns_name          = module.ecs.alb_dns_name
  alb_zone_id           = module.ecs.alb_zone_id
}

# Secrets Manager
module "secrets" {
  source = "./modules/secrets"
  
  environment = var.environment
}
