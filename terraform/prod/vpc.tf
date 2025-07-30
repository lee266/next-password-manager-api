
resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_support   = true
  enable_dns_hostnames = true

  tags = {
    Name = "password-manager-vpc"
  }
}

resource "aws_subnet" "public" {
  count                   = length(var.availability_zones)
  vpc_id                  = aws_vpc.main.id
  cidr_block              = cidrsubnet(var.vpc_cidr, 8, count.index)
  availability_zone       = var.availability_zones[count.index]
  map_public_ip_on_launch = true

  tags = {
    Name = "password-manager-public-subnet-${count.index + 1}"
  }
}

resource "aws_subnet" "private" {
  count             = length(var.availability_zones)
  vpc_id            = aws_vpc.main.id
  cidr_block        = cidrsubnet(var.vpc_cidr, 8, count.index + length(var.availability_zones))
  availability_zone = var.availability_zones[count.index]

  tags = {
    Name = "password-manager-private-subnet-${count.index + 1}"
  }
}

# -- ECR --

# PrivateLink: VPC Endpoint (API)
resource "aws_vpc_endpoint" "ecr_api" {
  vpc_id              = aws_vpc.main.id
  service_name        = "com.amazonaws.${var.aws_region}.ecr.api"
  vpc_endpoint_type   = "Interface"

  subnet_ids = [for subnet in aws_subnet.private : subnet.id]

  private_dns_enabled = true
  security_group_ids  = [aws_security_group.ecr_sg.id]

  tags = {
    Name = "ecr-api-endpoint"
  }
}

# PrivateLink: VPC Endpoint (Interface) for ECR (Docker registry)
resource "aws_vpc_endpoint" "ecr_dkr" {
  vpc_id              = aws_vpc.main.id
  service_name        = "com.amazonaws.${var.aws_region}.ecr.dkr"
  vpc_endpoint_type   = "Interface"

  subnet_ids = [for subnet in aws_subnet.private : subnet.id]

  private_dns_enabled = true
  security_group_ids  = [aws_security_group.ecr_sg.id]

  tags = {
    Name = "ecr-dkr-endpoint"
  }
}

# ECR was saved in S3, so we need to create a VPC Endpoint for S3
resource "aws_vpc_endpoint" "s3" {
  vpc_id              = aws_vpc.main.id
  service_name        = "com.amazonaws.${var.aws_region}.s3"
  vpc_endpoint_type   = "Gateway"

  route_table_ids = [aws_route_table.private.id]

  tags = {
    Name = "ecr-s3-endpoint"
  }
}

