import os
import logging
from typing import List, Optional
import boto3
from botocore.exceptions import ClientError
from ..exceptions import S3UploadError, CleanupError
from ..conf.settings import backup_settings

logger = logging.getLogger(__name__)

class S3BackupManager:
    def __init__(self, s3_config=None):
        self.s3_config = s3_config or backup_settings.s3_config
        self._client = None

    @property
    def client(self):
        if self._client is None and self.s3_config.enabled:
            self._client = boto3.client(
                's3',
                aws_access_key_id=self.s3_config.access_key_id,
                aws_secret_access_key=self.s3_config.secret_access_key
            )
        return self._client

    def upload(self, file_path: str) -> Optional[str]:
        """Upload file to S3 if enabled"""
        if not self.s3_config.enabled or not self.client:
            return None

        filename = os.path.basename(file_path)
        s3_key = f"{self.s3_config.backup_dir}/{filename}"

        try:
            try:
                self.client.head_object(Bucket=self.s3_config.bucket_name, Key=self.s3_config.backup_dir + '/')
            except ClientError as e:
                if e.response['Error']['Code'] == '404':
                    self.client.put_object(Bucket=self.s3_config.bucket_name, Key=self.s3_config.backup_dir + '/')
                    logger.debug(f"Created S3 folder: {self.s3_config.backup_dir}/")

            self.client.upload_file(file_path, self.s3_config.bucket_name, s3_key)
            logger.info(f"Uploaded to S3: s3://{self.s3_config.bucket_name}/{s3_key}")
            return s3_key

        except Exception as e:
            logger.error(f"S3 upload failed: {e}")
            raise S3UploadError(f"S3 upload failed: {e}")

    def cleanup_s3(self) -> List[str]:
        """Clean old S3 backups if enabled"""
        if not self.s3_config.enabled or not self.client:
            return []

        prefix = f"{self.s3_config.backup_dir}/"
        deleted = []
        
        try:
            objects = self.client.list_objects_v2(
                Bucket=self.s3_config.bucket_name,
                Prefix=prefix
            ).get('Contents', [])
            
            backups = sorted(
                [obj for obj in objects if obj['Key'].endswith('.sql')],
                key=lambda x: x['LastModified']
            )
            
            if len(backups) > self.s3_config.max_backups:
                for obj in backups[:-self.s3_config.max_backups]:
                    self.client.delete_object(
                        Bucket=self.s3_config.bucket_name,
                        Key=obj['Key']
                    )
                    deleted.append(obj['Key'])
                    logger.info(f"Deleted S3 backup: {obj['Key']}")
                    
        except Exception as e:
            logger.error(f"S3 cleanup failed: {e}")
            raise CleanupError(f"S3 cleanup failed: {e}")
            
        return deleted