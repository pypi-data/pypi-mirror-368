# Django DB S3 Backup

A robust Django library for automated PostgreSQL database backups with local and S3 storage support, featuring scheduled backups and restoration capabilities.

## Features

- 🗄️ Automated database backups
- ⏰ Scheduled backups using cron syntax
- 💾 Local backup storage with rotation
- ☁️ S3 backup storage with rotation
- 🔄 Easy restoration process
- 🔒 Secure credential management

## Installation

```bash
pip install django-db-s3-backup



## Configuration
#Add to your INSTALLED_APPS
INSTALLED_APPS = [
    ...
    'django_db_s3_backup.apps.DBS3BackupConfig',
    'django_apscheduler', 
    ...
]


#Database Configuration
# Optional - falls back to default Django DB settings if not specified
DB_BACKUP_HOST = 'backup.db.example.com'
DB_BACKUP_PORT = '5432'
DB_BACKUP_NAME = 'backup_db'
DB_BACKUP_USER = 'backup_user'
DB_BACKUP_PASSWORD = 'securepassword'


#Local Storage
DB_BACKUP_LOCAL_DIR = os.path.join(BASE_DIR, 'db_backups')  # Local backup directory
DB_BACKUP_MAX_LOCAL = 5  # Max local backups to keep


#S3 Storage

DB_BACKUP_S3_ENABLED = True  # Set False to disable S3
DB_BACKUP_S3_BUCKET_NAME = 'your-backup-bucket'
DB_BACKUP_S3_ACCESS_KEY = 'your-access-key'  # Consider using env vars
DB_BACKUP_S3_SECRET_KEY = 'your-secret-key'  # Consider using env vars
DB_BACKUP_S3_DIR = 'backups'  # S3 path prefix
DB_BACKUP_MAX_S3 = 30  # Max S3 backups to keep



#Scheduling
DB_BACKUP_SCHEDULE_ENABLED = True  # Enable scheduled backups, False by default
DB_BACKUP_SCHEDULE_CRON = '0 2 * * *'  # 2 AM daily (cron syntax)
