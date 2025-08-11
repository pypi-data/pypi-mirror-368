from django.conf import settings
import os
from .defaults import DatabaseConfig, S3Config, LocalConfig, ScheduleConfig

class BackupSettings:
    def __init__(self):
        self._configured = False
        self.db_config = DatabaseConfig()
        self.s3_config = S3Config()
        self.local_config = LocalConfig()
        self.schedule_config = ScheduleConfig()

    def configure(self):
        if self._configured:
            return

        # Get default database configuration from Django settings
        default_db = settings.DATABASES.get('default', {})
        
        self.db_config = DatabaseConfig(
            host=self._get_setting('DB_BACKUP_HOST', default_db.get('HOST', 'localhost')),
            port=self._get_setting('DB_BACKUP_PORT', default_db.get('PORT', '5432')),
            name=self._get_setting('DB_BACKUP_NAME', default_db.get('NAME', '')),
            user=self._get_setting('DB_BACKUP_USER', default_db.get('USER', '')),
            password=self._get_setting('DB_BACKUP_PASSWORD', default_db.get('PASSWORD', ''))
        )

        self.local_config = LocalConfig(
            backup_dir=getattr(settings, 'DB_BACKUP_LOCAL_DIR', os.path.join(settings.BASE_DIR, 'backups')),
            max_backups=getattr(settings, 'DB_BACKUP_MAX_LOCAL', 3)
        )

        self.s3_config = S3Config(
            enabled=getattr(settings, 'DB_BACKUP_S3_ENABLED', False),
            bucket_name=getattr(settings, 'DB_BACKUP_S3_BUCKET_NAME', ''),
            access_key_id=getattr(settings, 'DB_BACKUP_S3_ACCESS_KEY', ''),
            secret_access_key=getattr(settings, 'DB_BACKUP_S3_SECRET_KEY', ''),
            backup_dir=getattr(settings, 'DB_BACKUP_S3_DIR', 'backups'),
            max_backups=getattr(settings, 'DB_BACKUP_MAX_S3', 10)
        )

        self.schedule_config = ScheduleConfig(
            enabled=getattr(settings, 'DB_BACKUP_SCHEDULE_ENABLED', False),
            cron=getattr(settings, 'DB_BACKUP_SCHEDULE_CRON', '0 2 * * *'),
            options=getattr(settings, 'DB_BACKUP_SCHEDULE_OPTIONS', {})
        )

        self._configured = True

    def _get_setting(self, primary_key, fallback_value=None):
        return getattr(settings, primary_key, fallback_value)

backup_settings = BackupSettings()