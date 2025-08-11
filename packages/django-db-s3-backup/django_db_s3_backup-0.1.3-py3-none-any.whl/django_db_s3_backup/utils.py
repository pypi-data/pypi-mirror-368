import os
import shutil
import logging
import platform
from typing import Tuple, Optional

logger = logging.getLogger(__name__)

# Platform detection
IS_WINDOWS = platform.system() == 'Windows'

if not IS_WINDOWS:
    try:
        import pwd
        import grp
    except ImportError:
        IS_WINDOWS = True  # Fallback if somehow on non-Windows but without these modules

def get_owner_group(path: str) -> Tuple[str, str]:
    """Get owner and group of a file/directory"""
    if IS_WINDOWS:
        return "owner", "group"  # Default values for Windows
    
    try:
        stat_info = os.stat(path)
        uid = stat_info.st_uid
        gid = stat_info.st_gid
        return pwd.getpwuid(uid).pw_name, grp.getgrgid(gid).gr_name
    except Exception as e:
        logger.warning(f"Could not get owner/group: {e}")
        return "owner", "group"

def ensure_backup_dir(backup_dir: str, user: Optional[str] = None, group: Optional[str] = None):
    """Ensure backup directory exists with correct permissions"""
    os.makedirs(backup_dir, exist_ok=True)
    logger.info(f"Created backup directory: {backup_dir}")
    
    if not IS_WINDOWS and user and group:
        try:
            current_owner, current_group = get_owner_group(backup_dir)
            if current_owner != user or current_group != group:
                shutil.chown(backup_dir, user=user, group=group)
                logger.info(f"Changed ownership of {backup_dir} to {user}:{group}")
        except Exception as e:
            logger.warning(f"Could not change ownership: {e}")

def find_pg_dump() -> str:
    """Find pg_dump executable or return 'docker' if not found"""
    # First try Windows-specific locations
    if IS_WINDOWS:
        possible_paths = [
            os.path.join(os.environ.get("ProgramFiles", ""), "PostgreSQL"),
            os.path.join(os.environ.get("ProgramFiles(x86)", ""), "PostgreSQL")
        ]
        for path in possible_paths:
            if os.path.exists(path):
                for version_dir in os.listdir(path):
                    pg_dump_path = os.path.join(path, version_dir, "bin", "pg_dump.exe")
                    if os.path.exists(pg_dump_path):
                        logger.info(f"Found pg_dump at: {pg_dump_path}")
                        return pg_dump_path
    
    # Try system PATH
    pg_dump_path = shutil.which("pg_dump")
    if pg_dump_path:
        logger.info(f"Found pg_dump at: {pg_dump_path}")
        return pg_dump_path
    
    logger.warning("pg_dump not found in system PATH. Falling back to Docker.")
    return "docker"