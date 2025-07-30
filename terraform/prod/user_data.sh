#!/bin/bash

set -euxo pipefail

# Update packages
dnf update -y

# Install common tools
# dnf swap libcurl-minimal libcurl-full
dnf install -y git vim jq

# Install docker
dnf install -y docker
systemctl enable --now docker
usermod -aG docker ec2-user

# Install docker compose
curl -L "https://github.com/docker/compose/releases/download/v2.38.2/docker-compose-linux-x86_64" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose
ln -s /usr/local/bin/docker-compose /usr/bin/docker-compose || true

# Parameter Storeから設定値を取得
echo "Fetching application configuration from Parameter Store..."
CERTBOT_EMAIL=$(aws ssm get-parameter --region ap-northeast-1 --name "/password-manager/app/certbot-email" --query 'Parameter.Value' --output text)
DOMAIN_NAME=$(aws ssm get-parameter --region ap-northeast-1 --name "/password-manager/app/domain-name" --query 'Parameter.Value' --output text)
DB_HOST=$(aws ssm get-parameter --region ap-northeast-1 --name "/password-manager/app/db-host" --query 'Parameter.Value' --output text)
DB_PASSWORD=$(aws ssm get-parameter --region ap-northeast-1 --name "/password-manager/db/root-password" --with-decryption --query 'Parameter.Value' --output text)
DB_NAME=$(aws ssm get-parameter --region ap-northeast-1 --name "/password-manager/db/database-name" --query 'Parameter.Value' --output text)
EMAIL_HOST_PASSWORD=$(aws ssm get-parameter --region ap-northeast-1 --name "/password-manager/app/email-host-password" --with-decryption --query 'Parameter.Value' --output text)

echo "Configuration retrieved successfully"
echo "Domain: $DOMAIN_NAME"
echo "Email: $CERTBOT_EMAIL"

# Clone the app repository
cd /home/ec2-user
if [ -d "app" ]; then
    echo "App directory exists, updating..."
    cd app
    sudo git pull || echo "Git pull failed, continuing..."
else
    echo "Cloning repository..."
    sudo git clone https://github.com/lee266/next-password-manager-api.git app
    cd app
fi

chown -R ec2-user:ec2-user /home/ec2-user/app

# Configure Git safe directory
sudo git config --global --add safe.directory /home/ec2-user/app

# Checkout to issue branch
sudo git fetch origin || echo "Git fetch failed, continuing..."
sudo git switch -c issue-31 origin/issue-31 || sudo git checkout issue-31 || echo "Branch checkout failed, using current branch"

# Install Certbot
dnf install -y epel-release
dnf install -y certbot

# Create .env file from Parameter Store values
sudo tee .env > /dev/null <<EOF
SECRET_KEY='Your SECRET_KEY'

# --MySQL--
MYSQL_ROOT_PASSWORD=$DB_PASSWORD
MYSQL_DATABASE=$DB_NAME
MYSQL_USER='root'
MYSQL_PASSWORD=$DB_PASSWORD
MYSQL_HOST=$DB_HOST

# --Email--
EMAIL_HOST='smtp.gmail.com'
EMAIL_PORT=587
EMAIL_HOST_USER='testerif0@gmail.com'
EMAIL_HOST_PASSWORD=$EMAIL_HOST_PASSWORD
EMAIL_USE_TLS=True
DEFAULT_FROM_EMAIL='testerif0@gmail.com'

# superuser setting
SUPERUSER_NAME='super'
SUPERUSER_EMAIL=$CERTBOT_EMAIL
SUPERUSER_PASSWORD=$DB_PASSWORD
EOF


chown ec2-user:ec2-user .env

# Issue SSL certificate
echo "Issuing SSL certificate for $DOMAIN_NAME..."
sudo certbot certonly --standalone -d "$DOMAIN_NAME" --email "$CERTBOT_EMAIL" --agree-tos --non-interactive

# Copy SSL certificates into app
sudo mkdir -p ./docker/nginx/config/
sudo cp -r /etc/letsencrypt/archive/"$DOMAIN_NAME"/ ./docker/nginx/config/
chown -R ec2-user:ec2-user ./docker/nginx/config/

# systemdサービスファイルを作成
sudo tee /etc/systemd/system/password-manager-app.service > /dev/null << 'EOF'
[Unit]
Description=Password Manager Application
Requires=docker.service
After=docker.service network.target

[Service]
Type=oneshot
RemainAfterExit=yes
User=ec2-user
WorkingDirectory=/home/ec2-user/app
ExecStart=/usr/local/bin/docker-compose -f docker-compose-production.yml up -d --build
ExecStop=/usr/local/bin/docker-compose -f docker-compose-production.yml down
TimeoutStartSec=300
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOF

# SSL証明書の自動更新設定
sudo tee /etc/systemd/system/certbot-renew.service > /dev/null << 'EOF'
[Unit]
Description=Certbot Renewal
After=network.target

[Service]
Type=oneshot
ExecStart=/usr/bin/certbot renew --quiet --post-hook "systemctl reload password-manager-app"
EOF

sudo tee /etc/systemd/system/certbot-renew.timer > /dev/null << EOF
[Unit]
Description=Run certbot renewal twice daily
Requires=certbot-renew.service

[Timer]
OnCalendar=*-*-* 00,12:00:00
RandomizedDelaySec=3600
Persistent=true

[Install]
WantedBy=timers.target
EOF

# サービスを有効化
sudo systemctl daemon-reload
sudo systemctl enable password-manager-app.service
sudo systemctl enable certbot-renew.timer
sudo systemctl start certbot-renew.timer

# アプリケーションを起動
echo "Starting application..."
sudo systemctl start password-manager-app.service

docker-compose exec django bash -c "python manage.py migrate && python manage.py superuser"

sudo systemctl restart password-manager-app.service

# 起動確認
sleep 30
if docker-compose -f docker-compose-production.yml ps | grep -q "Up"; then
    echo "Application started successfully"
    docker-compose -f docker-compose-production.yml ps
else
    echo "Application may have failed to start"
    docker-compose -f docker-compose-production.yml logs
fi


# ログ出力
echo "Application setup completed at $(date)" >> /var/log/app-setup.log
docker-compose -f docker-compose-production.yml ps >> /var/log/app-setup.log 2>&1 || echo "Failed to get container status" >> /var/log/app-setup.log
