from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'Delete all users and create a new superuser'

    def add_arguments(self, parser):
        parser.add_argument('--username', type=str, required=True, help='New admin username')
        parser.add_argument('--email', type=str, required=True, help='New admin email')
        parser.add_argument('--password', type=str, required=True, help='New admin password')

    def handle(self, *args, **options):
        username = options['username']
        email = options['email']
        password = options['password']

        # Delete all existing users
        user_count = User.objects.count()
        User.objects.all().delete()
        self.stdout.write(self.style.SUCCESS(f'Deleted {user_count} existing users'))

        # Create new superuser
        User.objects.create_superuser(
            username=username,
            email=email,
            password=password
        )
        self.stdout.write(self.style.SUCCESS(f'Created new superuser: {username}'))
