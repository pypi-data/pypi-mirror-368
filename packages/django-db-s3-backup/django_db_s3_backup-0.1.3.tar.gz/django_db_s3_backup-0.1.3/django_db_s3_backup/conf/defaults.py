from dataclasses import dataclass
from typing import Optional, Dict, Any

@dataclass
class DatabaseConfig:
    host: str = "localhost"
    port: str = "5432"
    name: str = ""
    user: str = ""
    password: str = ""

@dataclass
class S3Config:
    enabled: bool = False
    bucket_name: str = ""
    access_key_id: str = ""
    secret_access_key: str = ""
    backup_dir: str = "backups"
    max_backups: int = 10

@dataclass
class LocalConfig:
    backup_dir: str = "backups"
    max_backups: int = 3

@dataclass
class ScheduleConfig:
    enabled: bool = False
    cron: str = "0 2 * * *"  # Daily at 2 AM
    options: Dict[str, Any] = None