"""Process indexing queue"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from blog.models_seo import IndexingQueue, SEOHealthLog
from blog.seo_indexing import submit_indexnow
from blog.seo_utils import ping_google_sitemap, ping_bing_sitemap


class Command(BaseCommand):
    help = 'Process pending URLs in indexing queue'

    def handle(self, *args, **options):
        pending = IndexingQueue.objects.filter(processed_at__isnull=True).order_by('-priority', 'created_at')[:50]
        
        if not pending:
            self.stdout.write('No pending URLs')
            return
        
        urls = [item.url for item in pending]
        
        # Submit to IndexNow
        if submit_indexnow(urls):
            self.stdout.write(self.style.SUCCESS(f'✓ IndexNow: {len(urls)} URLs'))
            for item in pending:
                item.submitted_indexnow = True
                item.processed_at = timezone.now()
                item.save()
        
        self.stdout.write(self.style.SUCCESS(f'Processed {len(urls)} URLs'))
