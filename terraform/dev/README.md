# Development Terraform

## Getting Started

### 1. Apply Terraform and SSH into EC2

```bash
terraform apply
ssh -i <your-pem> ec2-user@<public-ip>
```

### 2. Obtain SSL Certificate (make sure DNS is properly set)

```bash
sudo certbot certonly --standalone -d password-manager-api.rito-dev.com --email `YOUR_CERTBOT_EMAIL` --agree-tos --non-interactive
sudo cp -r /etc/letsencrypt/archive/password-manager-api.rito-dev.com/ ./docker/nginx/config/
```

> Note:
>
> Make sure password-manager-api.rito-dev.com is updated to the current EC2 public IP. This is required for certbot to succeed.

### 3. Build and start services with Docker Compose

```bash
docker-compose up -d --build

# Check systems up
docker-compose ps
```

### 4. Apply database migrations and create superuser

```bash
docker-compose exec django bash -c "python manage.py migrate && python manage.py superuser"
```
