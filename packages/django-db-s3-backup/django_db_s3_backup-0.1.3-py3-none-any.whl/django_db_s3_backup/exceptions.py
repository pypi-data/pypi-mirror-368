class BackupError(Exception):
    """Base exception for backup-related errors"""
    pass

class S3UploadError(BackupError):
    """Exception raised for S3 upload failures"""
    pass

class BackupCreationError(BackupError):
    """Exception raised for backup creation failures"""
    pass

class CleanupError(BackupError):
    """Exception raised for cleanup failures"""
    pass