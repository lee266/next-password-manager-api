output "app_public_ip" {
  description = "Static public IP of the app instance"
  value       = aws_eip.app_eip.public_ip
}

output "app_instance_id" {
  description = "Instance ID of the app server"
  value       = aws_instance.app.id
}

output "db_instance_id" {
  description = "Instance ID of the database server"
  value       = aws_instance.db.id
}

output "ecr_repository_url" {
  description = "ECR repository URL"
  value       = aws_ecr_repository.db_image.repository_url
}

output "vpc_id" {
  description = "VPC ID"
  value       = aws_vpc.main.id
}
