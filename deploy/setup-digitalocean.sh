#!/bin/bash
#
# Digital Ocean Deployment Script for Agent Builder
# Run this script on your Digital Ocean droplet to set up the production environment
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
    exit 1
}

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    error "Please run as root (use sudo)"
fi

log "Starting Agent Builder deployment on Digital Ocean..."

# Update system
log "Updating system packages..."
apt-get update && apt-get upgrade -y

# Install required packages
log "Installing required packages..."
apt-get install -y \
    curl \
    wget \
    git \
    nginx \
    ufw \
    certbot \
    python3-certbot-nginx \
    htop \
    vim

# Install Docker
log "Installing Docker..."
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    rm get-docker.sh
    systemctl start docker
    systemctl enable docker
else
    log "Docker already installed"
fi

# Install Docker Compose
log "Installing Docker Compose..."
if ! command -v docker-compose &> /dev/null; then
    curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
else
    log "Docker Compose already installed"
fi

# Create application directory
log "Creating application directory..."
mkdir -p /opt/agent-builder
cd /opt/agent-builder

# Clone repository if not exists
if [ ! -d ".git" ]; then
    log "Cloning repository..."
    git clone https://github.com/dhruvp66572/Agent_builder.git .
else
    log "Updating repository..."
    git pull origin main
fi

# Create data directories
log "Creating data directories..."
mkdir -p {data/postgres,data/chroma,data/uploads,logs,ssl}

# Set up environment file
if [ ! -f ".env" ]; then
    log "Creating environment file from template..."
    cp .env.example .env
    warn "Please edit /opt/agent-builder/.env with your configuration"
else
    log "Environment file already exists"
fi

# Set up firewall
log "Configuring firewall..."
ufw default deny incoming
ufw default allow outgoing
ufw allow ssh
ufw allow 80
ufw allow 443
ufw --force enable

# Set up Nginx
log "Configuring Nginx..."
mkdir -p /etc/nginx/sites-available
mkdir -p /etc/nginx/sites-enabled

# Create Nginx configuration
cat > /etc/nginx/sites-available/agentbuilder << 'EOF'
server {
    listen 80;
    server_name _;  # Replace with your domain
    
    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name _;  # Replace with your domain
    
    # SSL configuration (uncomment after obtaining certificates)
    # ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    # ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    
    # For now, use self-signed certificates or disable SSL
    ssl_certificate /opt/agent-builder/ssl/cert.pem;
    ssl_certificate_key /opt/agent-builder/ssl/key.pem;
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    
    # Frontend (React app)
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }
    
    # Backend API
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        
        # Increase timeout for file uploads
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
        client_max_body_size 50M;
    }
    
    # Health check endpoint
    location /health {
        proxy_pass http://localhost:8000/health;
    }
    
    # Static files
    location /static/ {
        alias /opt/agent-builder/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
EOF

# Enable site
ln -sf /etc/nginx/sites-available/agentbuilder /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Generate self-signed certificate for initial setup
log "Generating self-signed SSL certificate..."
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout /opt/agent-builder/ssl/key.pem \
    -out /opt/agent-builder/ssl/cert.pem \
    -subj "/C=US/ST=State/L=City/O=Organization/OU=OrgUnit/CN=localhost"

# Test Nginx configuration
nginx -t

# Start services
log "Starting services..."
systemctl restart nginx
systemctl enable nginx

# Set up log rotation
log "Setting up log rotation..."
cat > /etc/logrotate.d/agentbuilder << 'EOF'
/opt/agent-builder/logs/*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 644 root root
    postrotate
        docker-compose -f /opt/agent-builder/docker-compose.yml restart backend frontend
    endscript
}
EOF

# Create systemd service for auto-start
log "Creating systemd service..."
cat > /etc/systemd/system/agentbuilder.service << 'EOF'
[Unit]
Description=Agent Builder Application
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/opt/agent-builder
ExecStart=/usr/local/bin/docker-compose up -d
ExecStop=/usr/local/bin/docker-compose down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable agentbuilder

# Set up monitoring script
log "Setting up monitoring script..."
cat > /opt/agent-builder/monitor.sh << 'EOF'
#!/bin/bash
# Simple monitoring script for Agent Builder

check_service() {
    if docker-compose ps | grep -q "Up"; then
        echo "✓ Services are running"
    else
        echo "✗ Some services are down"
        docker-compose ps
        return 1
    fi
}

check_health() {
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        echo "✓ Backend health check passed"
    else
        echo "✗ Backend health check failed"
        return 1
    fi
}

check_disk() {
    DISK_USAGE=$(df /opt/agent-builder | awk 'NR==2{print $5}' | cut -d'%' -f1)
    if [ $DISK_USAGE -gt 80 ]; then
        echo "⚠ Disk usage is at ${DISK_USAGE}%"
        return 1
    else
        echo "✓ Disk usage is at ${DISK_USAGE}%"
    fi
}

echo "=== Agent Builder Monitoring - $(date) ==="
check_service && check_health && check_disk
echo "========================================="
EOF

chmod +x /opt/agent-builder/monitor.sh

# Add monitoring to cron
(crontab -l 2>/dev/null; echo "*/5 * * * * /opt/agent-builder/monitor.sh >> /opt/agent-builder/logs/monitor.log 2>&1") | crontab -

log "Deployment setup completed!"
echo
warn "Next steps:"
echo "1. Edit /opt/agent-builder/.env with your configuration"
echo "2. Update the domain name in /etc/nginx/sites-available/agentbuilder"
echo "3. Obtain SSL certificates: certbot --nginx -d yourdomain.com"
echo "4. Start the application: cd /opt/agent-builder && docker-compose up -d"
echo "5. Check logs: docker-compose logs -f"
echo
log "Your Agent Builder instance will be available at: https://your-domain.com"