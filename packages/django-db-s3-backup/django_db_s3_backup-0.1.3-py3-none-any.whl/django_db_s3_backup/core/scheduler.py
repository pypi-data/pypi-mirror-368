import uuid
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from django_apscheduler.jobstores import DjangoJobStore
import logging
from ..conf.settings import backup_settings
from .operations import BackupService
from django.db import connection

logger = logging.getLogger(__name__)

_scheduler = None

def start_backup_scheduler():
    global _scheduler
    
    if not backup_settings.schedule_config.enabled:
        print("Backup scheduling is disabled")
        return

    if _scheduler and _scheduler.running:
        print("Scheduler already running")
        return

    try:
        _scheduler = BackgroundScheduler(
            jobstores={'default': DjangoJobStore()},
            job_defaults={
                'coalesce': True,
                'max_instances': 1,
                'misfire_grace_time': 3600
            }
        )
        
        service = BackupService()
        
        _scheduler.add_job(
            _run_scheduled_backup,
            args=[service],
            trigger=CronTrigger.from_crontab(backup_settings.schedule_config.cron),
            id=f'db_backup_{uuid.uuid4().hex}',
            replace_existing=True
        )

        _scheduler.start()
        print(f"Scheduler started! Run Schedule: {backup_settings.schedule_config.cron}")
    except Exception as e:
        connection.close()
        print(f"Scheduler failed: {e}")
        raise

def _run_scheduled_backup(service):
    from django.db import connection
    try:
        service.execute(
            cleanup_local=True,
            upload_s3=backup_settings.s3_config.enabled,
            cleanup_s3=backup_settings.s3_config.enabled
        )
        print("Backup completed!")
    except Exception as e:
        print(f"Backup failed: {e}")
    finally:
        connection.close()