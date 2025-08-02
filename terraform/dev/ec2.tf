data "aws_ami" "amazon_linux" {
  most_recent = true

  owners = ["amazon"]

  filter {
    name   = "name"
    values = ["amzn2-ami-hvm-*-x86_64-gp2"]
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

  user_data = file("./user_data.sh")

  tags = {
    Name      = "password-manager-instance"
    AutoStart = "true"
    AutoStop  = "true"
  }
}
