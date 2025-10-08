#!/bin/bash
# Restore database from S3 backup

set -e

if [ -z "$1" ]; then
    echo "Usage: $0 <backup-file-name>"
    echo "Example: $0 leather_api_backup_20250115_120000.sql.gz"
    echo ""
    echo "Available backups:"
    aws s3 ls s3://${S3_BACKUP_BUCKET:-leather-api-backups}/daily/ | tail -10
    exit 1
fi

BACKUP_FILE=$1
S3_BUCKET="${S3_BACKUP_BUCKET:-leather-api-backups}"
TEMP_FILE="/tmp/$BACKUP_FILE"

echo "⚠️  WARNING: This will restore database from backup"
echo "Backup file: $BACKUP_FILE"
read -p "Continue? (yes/no): " CONFIRM

if [ "$CONFIRM" != "yes" ]; then
    echo "Restore cancelled"
    exit 0
fi

# Download backup
echo "Downloading backup from S3..."
aws s3 cp s3://$S3_BUCKET/daily/$BACKUP_FILE $TEMP_FILE

# Get database credentials
if [ -z "$DATABASE_URL" ]; then
    SECRET=$(aws secretsmanager get-secret-value --secret-id leather-api/production/db --query SecretString --output text)
    DB_HOST=$(echo $SECRET | jq -r '.host')
    DB_PORT=$(echo $SECRET | jq -r '.port')
    DB_NAME=$(echo $SECRET | jq -r '.dbname')
    DB_USER=$(echo $SECRET | jq -r '.username')
    DB_PASS=$(echo $SECRET | jq -r '.password')
else
    DB_HOST=$(echo $DATABASE_URL | sed -n 's/.*@\(.*\):.*/\1/p')
    DB_PORT=$(echo $DATABASE_URL | sed -n 's/.*:\([0-9]*\)\/.*/\1/p')
    DB_NAME=$(echo $DATABASE_URL | sed -n 's/.*\/\(.*\)/\1/p')
    DB_USER=$(echo $DATABASE_URL | sed -n 's/.*:\/\/\(.*\):.*/\1/p')
    DB_PASS=$(echo $DATABASE_URL | sed -n 's/.*:\/\/.*:\(.*\)@.*/\1/p')
fi

# Create backup of current database before restore
echo "Creating safety backup of current database..."
SAFETY_BACKUP="safety_backup_$(date +%Y%m%d_%H%M%S).sql.gz"
PGPASSWORD=$DB_PASS pg_dump -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME | gzip > /tmp/$SAFETY_BACKUP
aws s3 cp /tmp/$SAFETY_BACKUP s3://$S3_BUCKET/safety/$SAFETY_BACKUP
rm /tmp/$SAFETY_BACKUP

# Restore database
echo "Restoring database..."
gunzip < $TEMP_FILE | PGPASSWORD=$DB_PASS psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME

# Cleanup
rm $TEMP_FILE

echo "✅ Database restored from $BACKUP_FILE"
echo "Safety backup saved to: s3://$S3_BUCKET/safety/$SAFETY_BACKUP"
