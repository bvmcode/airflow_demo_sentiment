terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.0"
    }
  }
}


provider "aws" {
  region = "us-east-1"
  profile = "default"
}


data "aws_availability_zones" "available" {}

module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "2.77.0"

  name                 = "freightwaves_demo"
  cidr                 = "10.0.0.0/16"
  azs                  = data.aws_availability_zones.available.names
  public_subnets       = ["10.0.4.0/24", "10.0.5.0/24", "10.0.6.0/24"]
  enable_dns_hostnames = true
  enable_dns_support   = true
}

resource "aws_db_subnet_group" "freightwaves_demo" {
  name       = "freightwaves_demo"
  subnet_ids = module.vpc.public_subnets

  tags = {
    Name = "freightwaves_demo"
  }
}

resource "aws_security_group" "rds" {
  name   = "freightwaves_demo_rds"
  vpc_id = module.vpc.vpc_id

  ingress {
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "freightwaves_demo_rds"
  }
}

resource "aws_db_parameter_group" "freightwaves_demo" {
  name   = "freightwaves"
  family = "postgres14"

  parameter {
    name  = "log_connections"
    value = "1"
  }
}

resource "aws_db_instance" "freightwaves_demo" {
  identifier             = "freightwaves"
  instance_class         = "db.t3.micro"
  allocated_storage      = 5
  engine                 = "postgres"
  engine_version         = "14.5"
  username               = "freightwaves"
  password               = var.db_password
  db_subnet_group_name   = aws_db_subnet_group.freightwaves_demo.name
  vpc_security_group_ids = [aws_security_group.rds.id]
  parameter_group_name   = aws_db_parameter_group.freightwaves_demo.name
  publicly_accessible    = true
  skip_final_snapshot    = true
}