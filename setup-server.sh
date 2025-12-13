#!/bin/bash
# Server Setup Script for AWS Lightsail
# Run on the Lightsail instance after SSH

set -e

echo "========================================"
echo "  Setting up basamaljanaby server"
echo "========================================"

# Update system
echo "[1/6] Updating system..."
sudo apt-get update && sudo apt-get upgrade -y

# Install Docker
echo "[2/6] Installing Docker..."
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker ubuntu

# Install Docker Compose
echo "[3/6] Installing Docker Compose..."
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Install Nginx and Certbot
echo "[4/6] Installing Nginx and Certbot..."
sudo apt-get install -y nginx certbot python3-certbot-nginx

# Clone repository
echo "[5/6] Cloning repository..."
cd /home/ubuntu
git clone https://github.com/aliabbas19/test.git app
cd app

# Create .env file
echo "[6/6] Creating .env file..."
cat > backend/.env << 'EOF'
# UPDATE THESE VALUES!
DATABASE_URL=postgresql://basamaljanaby:ChangeThisPassword123@YOUR_DB_ENDPOINT:5432/basamaljanaby
SECRET_KEY=your-super-secret-key-change-this-in-production
DEBUG=false
BACKEND_URL=https://api.basamaljanaby.com
AWS_REGION=me-south-1
S3_BUCKET_NAME=basamaljanaby-media
EOF

echo ""
echo "========================================"
echo "  Setup Complete!"
echo "========================================"
echo ""
echo "NEXT STEPS:"
echo ""
echo "1. Edit backend/.env with your database endpoint:"
echo "   nano backend/.env"
echo ""
echo "2. Start the application:"
echo "   docker-compose -f docker-compose.lightsail.yml up -d --build"
echo ""
echo "3. Setup SSL (after DNS is configured):"
echo "   sudo certbot --nginx -d basamaljanaby.com -d api.basamaljanaby.com -d www.basamaljanaby.com"
echo ""
echo "4. Check status:"
echo "   docker-compose -f docker-compose.lightsail.yml ps"
echo ""
