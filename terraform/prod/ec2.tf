# Elastic IP for app instance
resource "aws_eip" "app_eip" {
  domain = "vpc"

  tags = {
    Name = "password-manager-app-eip"
  }
}

# Associate Elastic IP with app instance
resource "aws_eip_association" "app_eip_assoc" {
  instance_id   = aws_instance.app.id
  allocation_id = aws_eip.app_eip.id
}

data "aws_ami" "amazon_linux" {
  most_recent = true
  owners = ["amazon"]

  # Amazon Linux 2023 AMI
  filter {
    name   = "name"
    values = ["al2023-ami-*-x86_64"]
  }

  filter {
    name   = "architecture"
    values = ["x86_64"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

resource "aws_instance" "app" {
  ami                    = data.aws_ami.amazon_linux.id
  instance_type          = var.instance_type
  vpc_security_group_ids = [aws_security_group.app_sg.id]
  key_name               = var.ec2_key_name
  subnet_id              = aws_subnet.public[0].id

  iam_instance_profile   = aws_iam_instance_profile.ec2_ecr_instance_profile.name

  user_data = file("./user_data.sh")

  root_block_device {
    volume_type = "gp3"
    volume_size = 30
    delete_on_termination = true
  }

  tags = {
    Name      = "password-manager-instance"
    AutoStart = "true"
    AutoStop  = "true"
  }
}

resource "aws_instance" "db" {
  ami                    = data.aws_ami.amazon_linux.id
  instance_type          = var.db_instance_type
  vpc_security_group_ids = [
    aws_security_group.db_sg.id,
    aws_security_group.ecr_sg.id
  ]
  key_name               = var.ec2_key_name
  subnet_id              = aws_subnet.private[0].id
  iam_instance_profile   = aws_iam_instance_profile.ec2_ecr_instance_profile.name

  user_data = file("./db_user_data.sh")

  root_block_device {
    volume_type           = "gp3"
    volume_size           = 30
    delete_on_termination = true
  }

  tags = {
    Name = "password-manager-db-instance"
    AutoStart = "true"
    AutoStop  = "true"
  }

  depends_on = [ aws_instance.app ]
}

resource "aws_iam_role" "ec2_ecr_role" {
  name = "ec2-ecr-access-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Effect = "Allow",
      Principal = {
        Service = "ec2.amazonaws.com"
      },
      Action = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_role_policy_attachment" "ec2_ecr_attach" {
  role       = aws_iam_role.ec2_ecr_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly"
}

resource "aws_iam_instance_profile" "ec2_ecr_instance_profile" {
  name = "ec2-ecr-instance-profile"
  role = aws_iam_role.ec2_ecr_role.name
}

# SSM Parameters for database secrets
resource "aws_ssm_parameter" "db_root_password" {
  name  = "/password-manager/db/root-password"
  type  = "SecureString"
  value = var.db_root_password

  tags = {
    Name = "password-manager-db-root-password"
  }
}

resource "aws_ssm_parameter" "db_name" {
  name  = "/password-manager/db/database-name"
  type  = "String"
  value = var.db_name

  tags = {
    Name = "password-manager-db-name"
  }
}

resource "aws_iam_role_policy" "ssm_access" {
  name = "ssm-parameter-access"
  role = aws_iam_role.ec2_ecr_role.name

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = [
          "ssm:GetParameter",
          "ssm:GetParameters"
        ],
        Resource = [
          "arn:aws:ssm:${var.aws_region}:*:parameter/password-manager/*"
        ]
      }
    ]
  })
}
