import os
import subprocess
import logging
from datetime import datetime
from pathlib import Path
from typing import Tuple
from ..exceptions import BackupCreationError
from ..utils import find_pg_dump, ensure_backup_dir
from ..conf.settings import backup_settings

logger = logging.getLogger(__name__)

class DatabaseBackup:
    def __init__(self, db_config=None):
        self.db_config = db_config or backup_settings.db_config

    def create_backup(self, backup_dir: str) -> Tuple[str, str]:
        """Create a PostgreSQL backup file"""
        ensure_backup_dir(backup_dir)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"postgres_backup_{timestamp}.sql"
        filepath = os.path.join(backup_dir, filename)
        
        pg_dump_path = find_pg_dump()
        env = os.environ.copy()
        env['PGPASSWORD'] = self.db_config.password

        try:
            if pg_dump_path == "docker":
                cmd = [
                    'docker', 'run', '--rm',
                    '--network=host',
                    'postgres:latest',
                    'pg_dump',
                    '-h', self.db_config.host,
                    '-p', self.db_config.port,
                    '-U', self.db_config.user,
                    '-d', self.db_config.name,
                    '-f', f"/backup/{filename}",
                    '-F', 'p',
                    '--no-owner',
                    '--no-acl'
                ]
            else:
                cmd = [
                    pg_dump_path,
                    '-h', self.db_config.host,
                    '-p', self.db_config.port,
                    '-U', self.db_config.user,
                    '-d', self.db_config.name,
                    '-f', filepath
                ]

            logger.debug(f"Executing: {' '.join(cmd)}")
            subprocess.run(cmd, env=env, check=True, capture_output=True, text=True)
            
            if os.path.exists(filepath) and os.path.getsize(filepath) > 0:
                logger.info(f"Created backup: {filepath} ({os.path.getsize(filepath)} bytes)")
                return filepath, filename
            
            raise BackupCreationError("Backup file is empty or not created")
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Backup failed: {e.stderr}")
            raise BackupCreationError(f"Backup process failed: {e.stderr}")