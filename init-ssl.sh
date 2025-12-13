#!/bin/bash
# SSL Initialization Script for basamaljanaby.com
# Run this ONCE on initial deployment to obtain SSL certificate

set -e

DOMAIN="basamaljanaby.com"
EMAIL="superseal24579@gmail.com"

echo "============================================"
echo "SSL Certificate Setup for $DOMAIN"
echo "============================================"

# Create required directories
mkdir -p certbot/www certbot/conf

echo "1. Starting temporary nginx for certificate verification..."

# Run a simple nginx container for ACME challenge
sudo docker run -d --rm \
    --name nginx-certbot-init \
    -p 80:80 \
    -v $(pwd)/certbot/www:/var/www/certbot \
    nginx:alpine \
    sh -c "mkdir -p /var/www/certbot/.well-known/acme-challenge && nginx -g 'daemon off;' &
    echo 'server { listen 80; location /.well-known/acme-challenge/ { root /var/www/certbot; } location / { return 200 \"SSL setup...\"; } }' > /etc/nginx/conf.d/default.conf && nginx -s reload && sleep infinity"

# Wait for nginx to start
sleep 5

echo "2. Requesting SSL certificate from Let's Encrypt..."

# Request certificate
sudo docker run --rm \
    -v $(pwd)/certbot/www:/var/www/certbot \
    -v $(pwd)/certbot/conf:/etc/letsencrypt \
    certbot/certbot certonly \
    --webroot \
    -w /var/www/certbot \
    -d $DOMAIN \
    -d www.$DOMAIN \
    --email $EMAIL \
    --agree-tos \
    --no-eff-email \
    --force-renewal

echo "3. Stopping temporary nginx..."
sudo docker stop nginx-certbot-init 2>/dev/null || true

echo "============================================"
echo "SSL Certificate obtained successfully!"
echo "============================================"
echo ""
echo "Now run: sudo docker compose -f docker-compose.prod.yml up -d --build"
echo ""
