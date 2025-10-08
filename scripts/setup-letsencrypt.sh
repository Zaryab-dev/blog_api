#!/bin/bash
# Setup Let's Encrypt SSL certificates

set -e

DOMAIN="api.zaryableather.com"
EMAIL="admin@zaryableather.com"

echo "Setting up Let's Encrypt for $DOMAIN"

# Create directories
mkdir -p ssl certbot/{conf,www}

# Get certificate
docker-compose -f docker-compose.prod.yml run --rm certbot certonly \
  --webroot \
  --webroot-path=/var/www/certbot \
  --email $EMAIL \
  --agree-tos \
  --no-eff-email \
  -d $DOMAIN

# Reload Nginx
docker-compose -f docker-compose.prod.yml exec nginx nginx -s reload

echo "✅ SSL certificate installed for $DOMAIN"
echo "Certificate will auto-renew via certbot container"
