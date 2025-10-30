#!/bin/bash
# Automated database backup to S3

set -e

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="leather_api_backup_${TIMESTAMP}.sql.gz"
S3_BUCKET="${S3_BACKUP_BUCKET:-leather-api-backups}"
RETENTION_DAYS_7=7
RETENTION_DAYS_30=30
RETENTION_DAYS_90=90

echo "Starting database backup: $BACKUP_FILE"

# Get database credentials from environment or AWS Secrets Manager
if [ -z "$DATABASE_URL" ]; then
    echo "Fetching database credentials from AWS Secrets Manager..."
    SECRET=$(aws secretsmanager get-secret-value --secret-id leather-api/production/db --query SecretString --output text)
    DB_HOST=$(echo $SECRET | jq -r '.host')
    DB_PORT=$(echo $SECRET | jq -r '.port')
    DB_NAME=$(echo $SECRET | jq -r '.dbname')
    DB_USER=$(echo $SECRET | jq -r '.username')
    DB_PASS=$(echo $SECRET | jq -r '.password')
else
    # Parse DATABASE_URL
    DB_HOST=$(echo $DATABASE_URL | sed -n 's/.*@\(.*\):.*/\1/p')
    DB_PORT=$(echo $DATABASE_URL | sed -n 's/.*:\([0-9]*\)\/.*/\1/p')
    DB_NAME=$(echo $DATABASE_URL | sed -n 's/.*\/\(.*\)/\1/p')
    DB_USER=$(echo $DATABASE_URL | sed -n 's/.*:\/\/\(.*\):.*/\1/p')
    DB_PASS=$(echo $DATABASE_URL | sed -n 's/.*:\/\/.*:\(.*\)@.*/\1/p')
fi

# Create backup
echo "Creating backup..."
PGPASSWORD=$DB_PASS pg_dump -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME | gzip > /tmp/$BACKUP_FILE

# Upload to S3
echo "Uploading to S3..."
aws s3 cp /tmp/$BACKUP_FILE s3://$S3_BUCKET/daily/$BACKUP_FILE

# Copy to retention folders
DAY_OF_WEEK=$(date +%u)
DAY_OF_MONTH=$(date +%d)

if [ "$DAY_OF_WEEK" -eq 7 ]; then
    aws s3 cp /tmp/$BACKUP_FILE s3://$S3_BUCKET/weekly/$BACKUP_FILE
fi

if [ "$DAY_OF_MONTH" -eq 1 ]; then
    aws s3 cp /tmp/$BACKUP_FILE s3://$S3_BUCKET/monthly/$BACKUP_FILE
fi

# Cleanup local file
rm /tmp/$BACKUP_FILE

# Cleanup old backups
echo "Cleaning up old backups..."
aws s3 ls s3://$S3_BUCKET/daily/ | while read -r line; do
    FILE_DATE=$(echo $line | awk '{print $1" "$2}')
    FILE_NAME=$(echo $line | awk '{print $4}')
    FILE_EPOCH=$(date -d "$FILE_DATE" +%s)
    CURRENT_EPOCH=$(date +%s)
    DAYS_OLD=$(( ($CURRENT_EPOCH - $FILE_EPOCH) / 86400 ))
    
    if [ $DAYS_OLD -gt $RETENTION_DAYS_7 ]; then
        aws s3 rm s3://$S3_BUCKET/daily/$FILE_NAME
    fi
done

echo "✅ Backup completed: s3://$S3_BUCKET/daily/$BACKUP_FILE"
