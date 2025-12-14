#!/bin/bash
# Server Setup Script - Run once after EC2 creation
# Adds Swap memory and optimizes system for Docker

set -e

echo "============================================"
echo "Server Optimization for Docker"
echo "============================================"

# Check if swap exists
if [ -f /swapfile ]; then
    echo "Swap already exists"
else
    echo "1. Creating 2GB Swap file..."
    sudo fallocate -l 2G /swapfile
    sudo chmod 600 /swapfile
    sudo mkswap /swapfile
    sudo swapon /swapfile
    
    # Make swap permanent
    echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
    
    echo "Swap created successfully!"
fi

# Optimize swap usage
echo "2. Optimizing swap settings..."
echo 'vm.swappiness=10' | sudo tee -a /etc/sysctl.conf
echo 'vm.vfs_cache_pressure=50' | sudo tee -a /etc/sysctl.conf
sudo sysctl -p

echo "3. Cleaning Docker..."
sudo docker system prune -af

echo "============================================"
echo "Server optimization complete!"
echo "============================================"
echo ""
echo "Current memory status:"
free -m
echo ""
echo "Now run: sudo docker compose -f docker-compose.prod.yml up -d --build"
