from django.apps import AppConfig
from django.core.signals import request_started
from django.db.models.signals import post_migrate
import logging
import os
import sys

logger = logging.getLogger(__name__)

class DBS3BackupConfig(AppConfig):
    name = 'django_db_s3_backup'
    verbose_name = "Database S3 Backup"
    
    def ready(self):
        """Initialize backup settings and scheduler"""
        if os.environ.get('RUN_MAIN') == 'true' or not os.environ.get('WERKZEUG_RUN_MAIN'):
            try:
                from django_db_s3_backup.conf.settings import backup_settings
                backup_settings.configure()
                
                print(f"\n🔧 Initializing Database S3 Backup (v{getattr(backup_settings, 'version', 'unknown')})")
                print(f"🔄 Scheduled backups {'enabled' if backup_settings.schedule_config.enabled else 'disabled'}")
                print(f"☁️  S3 backups {'enabled' if backup_settings.s3_config.enabled else 'disabled'}\n")
                
                if backup_settings.schedule_config.enabled:
                    from django_db_s3_backup.core.scheduler import start_backup_scheduler
                    
                    post_migrate.connect(self._start_scheduler, sender=self)
                    request_started.connect(self._start_scheduler, weak=False)
                    if 'runserver' in sys.argv:
                        from threading import Timer
                        Timer(1.0, self._start_scheduler).start()
                        
            except ImportError as e:
                print(f"Critical import error: {e}")
                logger.error(f"Import error in ready(): {e}")
                raise
            except Exception as e:
                print(f"Initialization error: {e}")
                logger.error(f"Error initializing backup scheduler: {e}")
                raise
    
    def _start_scheduler(self, **kwargs):
        """Delayed scheduler startup"""
        if getattr(self, '_scheduler_started', False):
            return
            
        from django_db_s3_backup.core.scheduler import start_backup_scheduler
        print("\n🚀 Starting backup scheduler...")
        start_backup_scheduler()
        self._scheduler_started = True