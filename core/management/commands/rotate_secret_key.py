"""Secret key rotation management command"""
from django.core.management.base import BaseCommand
from django.core.management.utils import get_random_secret_key
from pathlib import Path
import os


class Command(BaseCommand):
    help = 'Generate new SECRET_KEY for rotation'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--update-env',
            action='store_true',
            help='Update .env file with new key (backup created)'
        )
    
    def handle(self, *args, **options):
        new_key = get_random_secret_key()
        
        self.stdout.write(self.style.SUCCESS('\n=== Secret Key Rotation ===\n'))
        self.stdout.write(f"New SECRET_KEY: {new_key}\n")
        
        if options['update_env']:
            self.update_env_file(new_key)
        else:
            self.stdout.write(self.style.WARNING(
                '\nTo update .env file automatically, run:\n'
                'python manage.py rotate_secret_key --update-env\n'
            ))
            self.stdout.write(
                'Or manually update your .env file with the new key above.\n'
            )
        
        self.stdout.write(self.style.WARNING(
            '\n⚠ IMPORTANT: Zero-downtime rotation steps:\n'
            '1. Add OLD_SECRET_KEY=<current_key> to .env\n'
            '2. Update SECRET_KEY=<new_key> in .env\n'
            '3. Deploy with both keys active\n'
            '4. After 24-48 hours, remove OLD_SECRET_KEY\n'
        ))
    
    def update_env_file(self, new_key):
        """Update .env file with new secret key"""
        base_dir = Path(__file__).resolve().parent.parent.parent.parent
        env_file = base_dir / '.env'
        
        if not env_file.exists():
            self.stdout.write(self.style.ERROR('Error: .env file not found'))
            return
        
        # Create backup
        backup_file = base_dir / f'.env.backup.{int(os.path.getmtime(env_file))}'
        with open(env_file, 'r') as f:
            content = f.read()
        
        with open(backup_file, 'w') as f:
            f.write(content)
        
        self.stdout.write(self.style.SUCCESS(f'Backup created: {backup_file}'))
        
        # Update SECRET_KEY
        lines = content.split('\n')
        updated = False
        
        for i, line in enumerate(lines):
            if line.startswith('SECRET_KEY='):
                old_key = line.split('=', 1)[1]
                lines.insert(i, f'OLD_SECRET_KEY={old_key}')
                lines[i + 1] = f'SECRET_KEY={new_key}'
                updated = True
                break
        
        if updated:
            with open(env_file, 'w') as f:
                f.write('\n'.join(lines))
            
            self.stdout.write(self.style.SUCCESS('.env file updated successfully'))
        else:
            self.stdout.write(self.style.ERROR('Error: SECRET_KEY not found in .env'))
