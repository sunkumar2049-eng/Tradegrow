#!/bin/bash

# TradingGrow Database Backup Script
# This script creates automated database backups with rotation

set -e

# Configuration
DB_NAME="tradinggrow_prod"
DB_USER="tradinggrow"
DB_HOST="localhost"
BACKUP_DIR="/backups"
RETENTION_DAYS=7
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/tradinggrow_backup_$DATE.sql"

# Create backup directory if it doesn't exist
mkdir -p $BACKUP_DIR

# Function to log messages
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1"
}

# Function to create backup
create_backup() {
    log "Starting database backup..."
    
    if pg_dump -h $DB_HOST -U $DB_USER -d $DB_NAME > $BACKUP_FILE; then
        log "Backup created successfully: $BACKUP_FILE"
        
        # Compress the backup
        gzip $BACKUP_FILE
        log "Backup compressed: ${BACKUP_FILE}.gz"
        
        return 0
    else
        log "ERROR: Backup failed!"
        return 1
    fi
}

# Function to cleanup old backups
cleanup_old_backups() {
    log "Cleaning up backups older than $RETENTION_DAYS days..."
    
    find $BACKUP_DIR -name "tradinggrow_backup_*.sql.gz" -mtime +$RETENTION_DAYS -delete
    
    log "Cleanup completed"
}

# Function to upload to S3 (optional)
upload_to_s3() {
    if [ ! -z "$AWS_ACCESS_KEY_ID" ] && [ ! -z "$S3_BUCKET_NAME" ]; then
        log "Uploading backup to S3..."
        
        aws s3 cp "${BACKUP_FILE}.gz" "s3://$S3_BUCKET_NAME/backups/"
        
        if [ $? -eq 0 ]; then
            log "Backup uploaded to S3 successfully"
        else
            log "ERROR: S3 upload failed"
        fi
    fi
}

# Function to verify backup integrity
verify_backup() {
    log "Verifying backup integrity..."
    
    # Test if the backup can be read
    if gunzip -t "${BACKUP_FILE}.gz" 2>/dev/null; then
        log "Backup integrity verification passed"
        return 0
    else
        log "ERROR: Backup integrity verification failed"
        return 1
    fi
}

# Function to send notification (optional)
send_notification() {
    local status=$1
    local message=$2
    
    if [ ! -z "$WEBHOOK_URL" ]; then
        curl -X POST -H 'Content-type: application/json' \
            --data "{\"text\":\"TradingGrow Backup $status: $message\"}" \
            $WEBHOOK_URL
    fi
}

# Main execution
main() {
    log "TradingGrow backup script started"
    
    # Create backup
    if create_backup; then
        # Verify backup
        if verify_backup; then
            # Upload to S3 if configured
            upload_to_s3
            
            # Cleanup old backups
            cleanup_old_backups
            
            log "Backup process completed successfully"
            send_notification "SUCCESS" "Database backup completed successfully"
        else
            log "Backup verification failed"
            send_notification "FAILED" "Backup verification failed"
            exit 1
        fi
    else
        log "Backup creation failed"
        send_notification "FAILED" "Database backup creation failed"
        exit 1
    fi
}

# Execute main function
main

log "Backup script finished"