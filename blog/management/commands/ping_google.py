"""Management command to ping Google for sitemap"""
from django.core.management.base import BaseCommand
from blog.seo_utils import notify_search_engines
from blog.models_seo import SEOHealthLog


class Command(BaseCommand):
    help = 'Manually ping Google and Bing with sitemap'

    def handle(self, *args, **options):
        self.stdout.write('Pinging search engines...')
        
        results = notify_search_engines()
        
        for engine, success in results.items():
            SEOHealthLog.objects.create(
                action=f'{engine}_ping',
                status='success' if success else 'failed',
                response_message='Manual ping via command'
            )
            
            if success:
                self.stdout.write(self.style.SUCCESS(f'✓ {engine.capitalize()} pinged'))
            else:
                self.stdout.write(self.style.ERROR(f'✗ {engine.capitalize()} failed'))
        
        self.stdout.write(self.style.SUCCESS('Done!'))
