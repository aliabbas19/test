#!/bin/bash
# Auto-deploy script for basamaljanaby.com
# This script pulls latest changes from GitHub and rebuilds containers

set -e

cd /home/ubuntu/app

echo "$(date): Pulling latest changes..."
git pull origin main

echo "$(date): Checking if SSL is initialized..."
if [ ! -d "certbot/conf/live/basamaljanaby.com" ]; then
    echo "$(date): SSL not initialized. Run ./init-ssl.sh first!"
    exit 1
fi

echo "$(date): Rebuilding containers..."
docker compose -f docker-compose.prod.yml up -d --build

echo "$(date): Cleaning up old images..."
docker image prune -f

echo "$(date): Deployment complete!"
echo "Visit: https://basamaljanaby.com"
