#!/bin/bash

set -euxo pipefail

# Update packages
dnf update -y

# Install common tools
dnf install -y unzip

# Install docker
dnf install -y docker
systemctl enable --now docker
usermod -aG docker ec2-user
