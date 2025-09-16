#!/bin/bash
#
# Backup script for Agent Builder production deployment
# Run this script regularly to backup database and application data
#

set -e

# Configuration
BACKUP_DIR="/opt/backups"
APP_DIR="/opt/agent-builder"
DATE=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=7

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

# Create backup directory
mkdir -p $BACKUP_DIR

log "Starting Agent Builder backup..."

# Database backup
log "Backing up database..."
cd $APP_DIR
docker-compose exec -T database pg_dump -U postgres agent_builder | gzip > $BACKUP_DIR/db_$DATE.sql.gz

# Application data backup (ChromaDB, uploads)
log "Backing up application data..."
tar -czf $BACKUP_DIR/data_$DATE.tar.gz -C $APP_DIR data/ uploads/ || true

# Configuration backup
log "Backing up configuration..."
cp $APP_DIR/.env $BACKUP_DIR/.env_$DATE || warn "Environment file not found"
cp -r $APP_DIR/ssl $BACKUP_DIR/ssl_$DATE/ 2>/dev/null || warn "SSL directory not found"

# Clean old backups
log "Cleaning old backups (older than $RETENTION_DAYS days)..."
find $BACKUP_DIR -type f -mtime +$RETENTION_DAYS -delete

# Create backup manifest
log "Creating backup manifest..."
cat > $BACKUP_DIR/manifest_$DATE.txt << EOF
Agent Builder Backup Manifest
============================
Date: $(date)
Database: db_$DATE.sql.gz
Data: data_$DATE.tar.gz
Environment: .env_$DATE
SSL: ssl_$DATE/

Files in backup:
$(ls -la $BACKUP_DIR/*$DATE* 2>/dev/null || echo "No files found")

Disk usage:
$(df -h $BACKUP_DIR)
EOF

log "Backup completed successfully!"
log "Backup files:"
ls -la $BACKUP_DIR/*$DATE* 2>/dev/null || echo "No backup files found"

# Optional: Upload to object storage
if [ "$BACKUP_TO_SPACES" = "true" ]; then
    log "Uploading to DigitalOcean Spaces..."
    # Uncomment and configure these lines for Spaces backup
    # s3cmd put $BACKUP_DIR/*$DATE* s3://your-backup-bucket/agent-builder/
fi

log "Backup process complete!"