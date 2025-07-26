#!/bin/bash

yum update -y
yum install -y git curl unzip

# install docker
amazon-linux-extras install docker -y
systemctl start docker
systemctl enable docker
usermod -aG docker ec2-user

# install docker compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.38.2/docker-compose-linux-x86_64" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
ln -s /usr/local/bin/docker-compose /usr/bin/docker-compose || true

# consturuct app directory
cd /home/ec2-user
git clone https://github.com/lee266/next-password-manager-api.git app
cd app

git config --global --add safe.directory /home/ec2-user/app

git switch -c issue-31 origin/issue-31

sudo amazon-linux-extras install epel
sudo yum install -y certbot

# Load environment variables
cp .env.example .env
export $(grep CERTBOT_EMAIL .env | xargs)

# certbot requires a domain name to issue a certificate
sudo certbot certonly --standalone -d password-manager-api.rito-dev.com --email "$CERTBOT_EMAIL" --agree-tos --non-interactive
sudo cp -r /etc/letsencrypt/archive/password-manager-api.rito-dev.com/ ./docker/nginx/config/

# start docker compose
# docker-compose up -d --build
