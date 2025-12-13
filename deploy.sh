#!/bin/bash
# Auto-deploy script for basamaljanaby.com
# This script pulls latest changes from GitHub and rebuilds containers

cd /home/ubuntu/app

echo "$(date): Pulling latest changes..."
git pull origin main

echo "$(date): Rebuilding containers..."
docker compose up -d --build

echo "$(date): Deployment complete!"
