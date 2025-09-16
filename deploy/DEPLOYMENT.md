# Digital Ocean Deployment Guide

This guide walks you through deploying the Agent Builder application to Digital Ocean using Docker and GitHub Actions.

## Prerequisites

Before deploying, ensure you have:

1. **Digital Ocean Account** with a Droplet (Ubuntu 20.04 or 22.04 recommended)
2. **Domain name** (optional, but recommended for production)
3. **GitHub repository** with the Agent Builder code
4. **API Keys** for OpenAI, Google AI, and SerpAPI

## Server Requirements

### Minimum Requirements
- **CPU**: 2 cores
- **RAM**: 4GB
- **Storage**: 50GB SSD
- **OS**: Ubuntu 20.04/22.04 LTS

### Recommended for Production
- **CPU**: 4+ cores
- **RAM**: 8GB+
- **Storage**: 100GB+ SSD
- **Load Balancer** (if scaling)

## Quick Deployment

### 1. Create Digital Ocean Droplet

```bash
# Using doctl CLI
doctl compute droplet create agentbuilder-prod \
  --region nyc3 \
  --image ubuntu-22-04-x64 \
  --size s-2vcpu-4gb \
  --ssh-keys YOUR_SSH_KEY_ID
```

### 2. Initial Server Setup

SSH into your droplet and run the setup script:

```bash
# Download and run the setup script
wget https://raw.githubusercontent.com/dhruvp66572/Agent_builder/main/deploy/setup-digitalocean.sh
chmod +x setup-digitalocean.sh
sudo ./setup-digitalocean.sh
```

### 3. Configure Environment

Edit the environment file:

```bash
cd /opt/agent-builder
sudo nano .env
```

Fill in your configuration:

```env
# Database
POSTGRES_PASSWORD=your-secure-password

# API Keys
OPENAI_API_KEY=sk-your-openai-key
GOOGLE_API_KEY=your-google-key
SERPAPI_KEY=your-serpapi-key

# Security
SECRET_KEY=your-32-character-secret-key

# Domain
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
CORS_ORIGINS=https://yourdomain.com
REACT_APP_API_URL=https://yourdomain.com
```

### 4. Update Domain Configuration

Update the Nginx configuration:

```bash
sudo nano /etc/nginx/sites-available/agentbuilder
# Replace server_name _; with server_name yourdomain.com www.yourdomain.com;
```

### 5. Deploy Application

```bash
cd /opt/agent-builder
sudo docker-compose up -d
```

### 6. Set Up SSL (Production)

For production with a domain:

```bash
# Install SSL certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Test auto-renewal
sudo certbot renew --dry-run
```

## GitHub Actions Setup

### 1. Repository Secrets

Add these secrets to your GitHub repository (Settings → Secrets and variables → Actions):

```
DOCKER_USERNAME              # Docker Hub username
DOCKER_PASSWORD              # Docker Hub password or access token
DIGITALOCEAN_ACCESS_TOKEN    # DigitalOcean API token
DIGITALOCEAN_SSH_PRIVATE_KEY # Private SSH key for server access
DIGITALOCEAN_SERVER_IP       # Your droplet's IP address

# Optional: Environment-specific URLs
REACT_APP_API_URL           # Frontend API URL
```

### 2. Docker Hub Setup

1. Create repositories:
   - `yourusername/agentbuilder-backend`
   - `yourusername/agentbuilder-frontend`

2. Update the workflow file `.github/workflows/ci-cd.yml`:
   ```yaml
   env:
     REGISTRY: docker.io
     BACKEND_IMAGE_NAME: yourusername/agentbuilder-backend
     FRONTEND_IMAGE_NAME: yourusername/agentbuilder-frontend
   ```

### 3. Deployment Process

The GitHub Actions workflow will:

1. **Build & Test**: Run tests for both backend and frontend
2. **Create Docker Images**: Build and push images to Docker Hub
3. **Deploy**: SSH into your server and update the running containers
4. **Health Check**: Verify the deployment is successful

## Manual Deployment

If you prefer manual deployment:

### 1. Build and Push Images

```bash
# Backend
cd backend
docker build -t yourusername/agentbuilder-backend:latest .
docker push yourusername/agentbuilder-backend:latest

# Frontend
cd frontend
docker build -t yourusername/agentbuilder-frontend:latest .
docker push yourusername/agentbuilder-frontend:latest
```

### 2. Deploy on Server

```bash
# On your Digital Ocean droplet
cd /opt/agent-builder
docker-compose pull
docker-compose down
docker-compose up -d

# Run database migrations
docker-compose exec backend python -m alembic upgrade head
```

## Monitoring and Maintenance

### Health Checks

Check application status:

```bash
# Run monitoring script
/opt/agent-builder/monitor.sh

# Check container status
docker-compose ps

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Backup

Regular backup script:

```bash
#!/bin/bash
# backup.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/opt/backups"
mkdir -p $BACKUP_DIR

# Database backup
docker-compose exec -T database pg_dump -U postgres agent_builder > $BACKUP_DIR/db_$DATE.sql

# Application data backup
tar -czf $BACKUP_DIR/data_$DATE.tar.gz -C /opt/agent-builder data/

# Clean old backups (keep last 7 days)
find $BACKUP_DIR -type f -mtime +7 -delete

echo "Backup completed: $DATE"
```

### Updates

To update the application:

```bash
cd /opt/agent-builder
git pull origin main
docker-compose pull
docker-compose down
docker-compose up -d
docker-compose exec backend python -m alembic upgrade head
```

## Scaling

### Load Balancer Setup

For high-traffic applications, use Digital Ocean Load Balancer:

```bash
# Create load balancer
doctl compute load-balancer create \
  --name agentbuilder-lb \
  --region nyc3 \
  --forwarding-rules entry_protocol:https,entry_port:443,target_protocol:http,target_port:80 \
  --health-check protocol:http,port:80,path:/health
```

### Database Scaling

Consider managed PostgreSQL:

```bash
# Create managed database
doctl databases create agentbuilder-db \
  --engine postgres \
  --region nyc3 \
  --size db-s-1vcpu-1gb \
  --num-nodes 1
```

## Security Best Practices

1. **Regular Updates**: Keep system and containers updated
2. **Firewall**: Use UFW or Digital Ocean Cloud Firewall
3. **SSL/TLS**: Always use HTTPS in production
4. **Secrets Management**: Never commit secrets to git
5. **Database Security**: Use strong passwords and restrict access
6. **Monitoring**: Set up log monitoring and alerts

## Troubleshooting

### Common Issues

**Container won't start:**
```bash
docker-compose logs backend
# Check environment variables and database connection
```

**SSL Certificate Issues:**
```bash
sudo certbot certificates
sudo systemctl status nginx
```

**Database Connection Errors:**
```bash
# Check database container
docker-compose exec database psql -U postgres -d agent_builder
```

**High Memory Usage:**
```bash
# Restart containers
docker-compose restart
# Monitor resources
htop
```

### Log Locations

- **Application logs**: `/opt/agent-builder/logs/`
- **Nginx logs**: `/var/log/nginx/`
- **System logs**: `/var/log/syslog`
- **Docker logs**: `docker-compose logs [service]`

## Support

For deployment issues:
1. Check the [troubleshooting section](TROUBLESHOOTING.md)
2. Review application logs
3. Open an issue on GitHub

---

**Security Note**: Always review and customize the configuration for your specific security requirements before deploying to production.