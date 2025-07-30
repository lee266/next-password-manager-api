#!/bin/bash

set -euxo pipefail

# Update packages
sudo dnf update -y

# Install common tools
# sudo dnf swap libcurl-minimal libcurl-full
sudo dnf install -y git vim

# Install docker
sudo dnf install -y docker
sudo systemctl enable --now docker
sudo usermod -aG docker ec2-user

# Install docker compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.38.2/docker-compose-linux-x86_64" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
ln -s /usr/local/bin/docker-compose /usr/bin/docker-compose || true

# Clone the app repository
cd /home/ec2-user
git clone https://github.com/lee266/next-password-manager-api.git app
cd app
chown -R ec2-user:ec2-user /home/ec2-user/app

# Configure Git safe directory
sudo git config --global --add safe.directory /home/ec2-user/app

# Checkout to issue branch
sudo git switch -c issue-31 origin/issue-31

# Install Certbot

sudo dnf install -y epel-release
sudo dnf install -y certbot

# Load environment variables
sudo cp .env.example .env
export $(grep CERTBOT_EMAIL .env | xargs)

# Issue SSL certificate
# sudo certbot certonly --standalone -d password-manager-api.rito-dev.com --email "$CERTBOT_EMAIL" --agree-tos --non-interactive

# Copy SSL certificates into app
# sudo cp -r /etc/letsencrypt/archive/password-manager-api.rito-dev.com/ ./docker/nginx/config/

# Start application (you can uncomment after verifying)
# docker-compose up -d --build
