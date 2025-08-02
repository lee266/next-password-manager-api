#!/bin/bash

set -euxo pipefail

# Update packages
dnf update -y

# Install common tools
dnf install -y unzip jq

# Install docker
dnf install -y docker
systemctl enable --now docker
usermod -aG docker ec2-user

# Parameter Storeから設定値を取得
echo "Fetching database configuration from Parameter Store..."
DB_ROOT_PASSWORD=$(aws ssm get-parameter --region ap-northeast-1 --name "/password-manager/db/root-password" --with-decryption --query 'Parameter.Value' --output text)
DB_NAME=$(aws ssm get-parameter --region ap-northeast-1 --name "/password-manager/db/database-name" --query 'Parameter.Value' --output text)

# 取得確認（パスワードは非表示）
echo "Database name: $DB_NAME"
echo "Password retrieved successfully"

# ECRにログイン
echo "Logging in to ECR..."
aws ecr get-login-password --region ap-northeast-1 | docker login --username AWS --password-stdin 043309350986.dkr.ecr.ap-northeast-1.amazonaws.com/

# 既存のコンテナがあれば停止・削除
if docker ps -a --format 'table {{.Names}}' | grep -q password-manager-db 2>/dev/null; then
    echo "Stopping existing container..."
    docker stop password-manager-db || true
    docker rm password-manager-db || true
fi

# Dockerコンテナを起動
echo "Starting database container..."
docker run -d \
  --name password-manager-db \
  --restart unless-stopped \
  -p 3306:3306 \
  -e MYSQL_ROOT_PASSWORD="${DB_ROOT_PASSWORD}" \
  -e MYSQL_DATABASE="${DB_NAME}" \
  -v /var/lib/mysql:/var/lib/mysql \
  043309350986.dkr.ecr.ap-northeast-1.amazonaws.com/password-manager-db:latest

# systemdサービスファイルを作成（追加の保険として）
sudo tee /etc/systemd/system/password-manager-db.service > /dev/null << EOF
[Unit]
Description=Password Manager Database
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
User=root
ExecStart=/bin/bash -c 'docker start password-manager-db || docker run -d --name password-manager-db --restart unless-stopped -p 3306:3306 -e MYSQL_ROOT_PASSWORD="\$(aws ssm get-parameter --region ap-northeast-1 --name "/password-manager/db/root-password" --with-decryption --query Parameter.Value --output text)" -e MYSQL_DATABASE="\$(aws ssm get-parameter --region ap-northeast-1 --name "/password-manager/db/database-name" --query Parameter.Value --output text)" -v /var/lib/mysql:/var/lib/mysql 043309350986.dkr.ecr.ap-northeast-1.amazonaws.com/password-manager-db:latest'
ExecStop=/usr/bin/docker stop password-manager-db

[Install]
WantedBy=multi-user.target
EOF

# サービスを有効化
sudo systemctl daemon-reload
sudo systemctl enable password-manager-db.service

# 起動確認
sleep 10
if docker ps --format 'table {{.Names}}' | grep -q password-manager-db; then
    echo "Database container started successfully"
    docker ps | grep password-manager-db
else
    echo "Failed to start database container"
    docker logs password-manager-db || echo "No container logs available"
fi

# ログ出力
echo "Database setup completed at $(date)" >> /var/log/db-setup.log
echo "Container status:" >> /var/log/db-setup.log
docker ps | grep password-manager-db >> /var/log/db-setup.log 2>&1 || echo "Container not found" >> /var/log/db-setup.log
