from django.core.management.base import BaseCommand
from django_db_s3_backup.core.operations import BackupService
from django_db_s3_backup.exceptions import BackupError
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Creates a database backup, optionally uploads to S3, and cleans up old backups'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--no-upload',
            action='store_true',
            help='Skip uploading to S3 (overrides settings)',
        )
        parser.add_argument(
            '--upload-only',
            action='store_true',
            help='Only upload existing backups (no new backup)',
        )
        parser.add_argument(
            '--cleanup-local',
            action='store_true',
            help='Clean up old local backups (overrides settings)',
        )
        parser.add_argument(
            '--cleanup-s3',
            action='store_true',
            help='Clean up old S3 backups (overrides settings)',
        )
        parser.add_argument(
            '--debug',
            action='store_true',
            help='Enable debug output',
        )

    def handle(self, *args, **options):
        log_level = logging.DEBUG if options['debug'] else logging.INFO
        logging.basicConfig(level=log_level)
        
        try:
            service = BackupService()
            
            if options['upload_only']:
                self.stdout.write(self.style.WARNING('Skipping new backup creation (upload-only mode)'))
                result = {
                    'local_backup': None,
                    's3_upload': None,
                    's3_cleanup': None
                }
            else:
                self.stdout.write(self.style.SUCCESS('Starting database backup...'))
                result = service.execute(
                    cleanup_local=options['cleanup_local'],
                    upload_s3=not options['no_upload'],
                    cleanup_s3=options['cleanup_s3']
                )
            
            self._print_results(result)
            
            if not result.get('success', False):
                raise BackupError("Backup completed with errors")
                
            self.stdout.write(self.style.SUCCESS('Backup completed successfully!'))
            
        except BackupError as e:
            self.stdout.write(self.style.ERROR(f'Backup failed: {str(e)}'))
            logger.exception("Backup failed")
            raise

    def _print_results(self, result):
        """Format and print the backup results"""
        if result.get('local_backup'):
            self.stdout.write(
                self.style.SUCCESS(f"Created local backup: {result['local_backup']['path']} "
                                 f"({result['local_backup']['size']} bytes)"))
        
        if result.get('s3_upload'):
            self.stdout.write(
                self.style.SUCCESS(f"Uploaded to S3: {result['s3_upload']['key']}"))
        
        if result.get('local_cleanup') and result['local_cleanup']['deleted']:
            self.stdout.write(
                self.style.NOTICE(f"Cleaned up local backups: {len(result['local_cleanup']['deleted'])} deleted"))
        
        if result.get('s3_cleanup') and result['s3_cleanup']['deleted']:
            self.stdout.write(
                self.style.NOTICE(f"Cleaned up S3 backups: {len(result['s3_cleanup']['deleted'])} deleted"))
        
        if result.get('error'):
            self.stdout.write(self.style.ERROR(f"Error: {result['error']}"))