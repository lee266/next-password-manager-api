variable "aws_profile" {
  description = "AWS CLI profile to use"
  type        = string
  default     = "default"
}

variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "ap-northeast-1"
}

variable "instance_type" {
  description = "Instance type"
  type        = string
  default     = "t3.micro"
}

variable "db_instance_type" {
  description = "Database instance type"
  type        = string
  default     = "t3.micro"
}

variable "allowed_ssh_cidr_blocks" {
  description = "List of CIDR blocks allowed to SSH"
  type        = list(string)
  default     = ["0.0.0.0/0"]
}

variable "ec2_key_name" {
  description = "Key pair name for EC2 instances"
  type        = string
  default     = "password-manager-ec2"
}

# VPC/Subnet variables
variable "availability_zones" {
  description = "List of availability zones to use"
  type        = list(string)
  default     = ["ap-northeast-1a", "ap-northeast-1c"]
}

variable "vpc_cidr" {
  description = "CIDR block for VPC"
  type        = string
  default     = "10.0.0.0/16"
}

# Auto Start/Stop Schedule variables
variable "start_schedule" {
  description = "Cron expression for starting instances"
  type        = string
  default     = "cron(0 1 * * ? *)" # UTC 01:00 (JST 10:00)
}

variable "stop_schedule" {
  description = "Cron expression for stopping instances"
  type        = string
  default     = "cron(0 13 * * ? *)" # UTC 13:00 (JST 22:00)
}
