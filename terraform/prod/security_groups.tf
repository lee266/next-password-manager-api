resource "aws_security_group" "app_sg" {
  name        = "password-manager-sg"
  description = "Security group for Password Manager App"
  vpc_id      = aws_vpc.main.id
}

resource "aws_vpc_security_group_ingress_rule" "ssh" {
  security_group_id = aws_security_group.app_sg.id
  cidr_ipv4         = var.allowed_ssh_cidr_blocks[0]
  from_port         = 22
  ip_protocol       = "tcp"
  to_port           = 22
  description       = "Allow SSH from specific IP addresses"
}

resource "aws_vpc_security_group_ingress_rule" "http" {
  security_group_id = aws_security_group.app_sg.id
  cidr_ipv4         = "0.0.0.0/0"
  from_port         = 80
  ip_protocol       = "tcp"
  to_port           = 80
  description       = "Allow HTTP from anywhere"
}

resource "aws_vpc_security_group_ingress_rule" "https" {
  security_group_id = aws_security_group.app_sg.id
  cidr_ipv4         = "0.0.0.0/0"
  from_port         = 443
  ip_protocol       = "tcp"
  to_port           = 443
  description       = "HTTPs access from VPC CIDR"
}

resource "aws_vpc_security_group_egress_rule" "all" {
  security_group_id = aws_security_group.app_sg.id
  cidr_ipv4         = "0.0.0.0/0"
  from_port         = -1
  ip_protocol       = "-1"
  to_port           = -1
  description       = "Allow all outbound traffic"
}

resource "aws_security_group" "db_sg" {
  name        = "password-manager-db-sg"
  description = "Security group for Password Manager DB"
  vpc_id      = aws_vpc.main.id
}

resource "aws_security_group_rule" "db_ingress_from_app" {
  type                     = "ingress"
  from_port                = 3306
  to_port                  = 3306
  protocol                 = "tcp"
  security_group_id        = aws_security_group.db_sg.id
  source_security_group_id = aws_security_group.app_sg.id
  description              = "Allow MySQL access from app security group"
}

resource "aws_security_group_rule" "private_ec2_ssh_from_public_ec2" {
  type                     = "ingress"
  security_group_id        = aws_security_group.db_sg.id
  from_port                = 22
  to_port                  = 22
  protocol                 = "tcp"
  source_security_group_id = aws_security_group.app_sg.id
  description              = "Allow SSH from App security group"
}

resource "aws_security_group_rule" "db_egress_all" {
  type              = "egress"
  from_port         = -1
  to_port           = -1
  protocol          = "-1"
  security_group_id = aws_security_group.db_sg.id
  cidr_blocks       = ["0.0.0.0/0"]
  description       = "Allow all outbound traffic"
}

resource "aws_security_group" "ecr_sg" {
  name        = "password-manager-ecr-sg"
  description = "Security group for ECR access"
  vpc_id      = aws_vpc.main.id
}

resource "aws_vpc_security_group_ingress_rule" "https_for_ecr" {
  security_group_id = aws_security_group.ecr_sg.id
  cidr_ipv4         = aws_vpc.main.cidr_block
  from_port         = 443
  ip_protocol       = "tcp"
  to_port           = 443
  description       = "Allow HTTPS access from within VPC"
}

resource "aws_vpc_security_group_egress_rule" "all_for_ecr" {
  security_group_id = aws_security_group.ecr_sg.id
  cidr_ipv4         = "0.0.0.0/0"
  from_port         = -1
  ip_protocol       = "-1"
  to_port           = -1
  description       = "Allow all outbound traffic"
}
