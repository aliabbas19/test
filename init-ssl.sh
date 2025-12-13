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

# Create a temporary nginx config for initial certificate request
cat > nginx/nginx-init.conf << 'EOF'
events {
    worker_connections 1024;
}

http {
    server {
        listen 80;
        server_name basamaljanaby.com www.basamaljanaby.com;

        location /.well-known/acme-challenge/ {
            root /var/www/certbot;
        }

        location / {
            return 200 'SSL setup in progress...';
            add_header Content-Type text/plain;
        }
    }
}
EOF

echo "1. Starting temporary nginx for certificate verification..."

# Start nginx with temporary config (no SSL yet)
docker compose -f docker-compose.prod.yml run -d --rm \
    -v $(pwd)/nginx/nginx-init.conf:/etc/nginx/nginx.conf:ro \
    -v $(pwd)/certbot/www:/var/www/certbot:ro \
    -p 80:80 \
    --name nginx-init \
    nginx:alpine

# Wait for nginx to start
sleep 5

echo "2. Requesting SSL certificate from Let's Encrypt..."

# Request certificate
docker run --rm \
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
docker stop nginx-init 2>/dev/null || true

echo "4. Cleaning up temporary config..."
rm -f nginx/nginx-init.conf

echo "============================================"
echo "SSL Certificate obtained successfully!"
echo "============================================"
echo ""
echo "Now run: docker compose -f docker-compose.prod.yml up -d --build"
echo ""
