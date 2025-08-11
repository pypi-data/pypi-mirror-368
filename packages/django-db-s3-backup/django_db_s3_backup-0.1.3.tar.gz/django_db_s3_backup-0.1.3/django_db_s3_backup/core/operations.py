import os
import logging
from typing import Dict, List
from pathlib import Path
from .backup import DatabaseBackup
from .s3 import S3BackupManager
from ..conf.settings import backup_settings
from ..exceptions import BackupError

logger = logging.getLogger(__name__)

class BackupService:
    def __init__(self):
        self.db_backup = DatabaseBackup()
        self.s3_manager = S3BackupManager()

    def execute(
        self,
        backup_dir: str = None,
        cleanup_local: bool = True,
        upload_s3: bool = None,
        cleanup_s3: bool = None
    ) -> Dict:
        """
        Execute backup with flexible operations
        
        Returns:
            {
                "success": bool,
                "local_backup": {"path": str, "size": int},
                "s3_upload": {"key": str} if uploaded,
                "local_cleanup": {"deleted": List[str]},
                "s3_cleanup": {"deleted": List[str]},
                "error": str if failed
            }
        """
        backup_dir = backup_dir or backup_settings.local_config.backup_dir
        upload_s3 = upload_s3 if upload_s3 is not None else backup_settings.s3_config.enabled
        cleanup_s3 = cleanup_s3 if cleanup_s3 is not None else upload_s3
        
        result = {
            "success": False,
            "local_backup": None,
            "s3_upload": None,
            "local_cleanup": None,
            "s3_cleanup": None
        }

        try:
            backup_path, _ = self.db_backup.create_backup(backup_dir)
            result["local_backup"] = {
                "path": backup_path,
                "size": os.path.getsize(backup_path)
            }

            if cleanup_local:
                deleted = self._cleanup_local(backup_dir)
                result["local_cleanup"] = {"deleted": deleted}
            if upload_s3:
                s3_key = self.s3_manager.upload(backup_path)
                if s3_key:
                    result["s3_upload"] = {"key": s3_key}

                if cleanup_s3:
                    deleted = self.s3_manager.cleanup_s3()
                    result["s3_cleanup"] = {"deleted": deleted}

            result["success"] = True
            return result

        except Exception as e:
            logger.error(f"Backup failed: {e}")
            result["error"] = str(e)
            raise BackupError(f"Backup operation failed: {e}") from e

    def _cleanup_local(self, backup_dir: str) -> List[str]:
        """Clean up old local backups"""
        backups = sorted(Path(backup_dir).glob('postgres_backup_*.sql'), key=os.path.getmtime)
        max_backups = backup_settings.local_config.max_backups
        deleted = []
        
        if len(backups) > max_backups:
            for backup in backups[:-max_backups]:
                try:
                    os.remove(backup)
                    deleted.append(str(backup))
                    logger.info(f"Deleted local backup: {backup}")
                except Exception as e:
                    logger.error(f"Failed to delete {backup}: {e}")
                    raise
                    
        return deleted