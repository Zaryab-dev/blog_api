"""Verify SEO schema for all posts"""
from django.core.management.base import BaseCommand
from blog.models import Post
from blog.models_seo import SchemaMetadata
from blog.seo_schema_generator import generate_blog_posting_schema, sync_schema_to_db
import json


class Command(BaseCommand):
    help = 'Verify and sync SEO schema for all published posts'

    def add_arguments(self, parser):
        parser.add_argument(
            '--fix',
            action='store_true',
            help='Auto-fix missing or invalid schemas',
        )

    def handle(self, *args, **options):
        posts = Post.published.select_related('author', 'featured_image').prefetch_related('categories', 'tags')
        total = posts.count()
        
        self.stdout.write(f'Checking {total} published posts...\n')
        
        missing = []
        invalid = []
        valid = 0
        
        for post in posts:
            try:
                # Check if schema exists in DB
                schema_meta = SchemaMetadata.objects.filter(
                    object_type='post',
                    object_id=post.slug,
                    schema_type='BlogPosting',
                    is_active=True
                ).first()
                
                if not schema_meta:
                    missing.append(post.slug)
                    if options['fix']:
                        schema = generate_blog_posting_schema(post)
                        sync_schema_to_db(post, 'BlogPosting', schema)
                        self.stdout.write(self.style.SUCCESS(f'✓ Fixed: {post.slug}'))
                else:
                    # Validate JSON structure
                    schema_data = schema_meta.json_data
                    if not schema_data.get('@context') or not schema_data.get('@type'):
                        invalid.append(post.slug)
                        if options['fix']:
                            schema = generate_blog_posting_schema(post)
                            sync_schema_to_db(post, 'BlogPosting', schema)
                            self.stdout.write(self.style.WARNING(f'⚠ Fixed invalid: {post.slug}'))
                    else:
                        valid += 1
            
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'✗ Error {post.slug}: {str(e)}'))
        
        # Summary
        self.stdout.write('\n' + '='*50)
        self.stdout.write(f'Total Posts: {total}')
        self.stdout.write(self.style.SUCCESS(f'Valid Schemas: {valid}'))
        
        if missing:
            self.stdout.write(self.style.WARNING(f'Missing Schemas: {len(missing)}'))
            if not options['fix']:
                self.stdout.write('  Run with --fix to auto-generate')
        
        if invalid:
            self.stdout.write(self.style.ERROR(f'Invalid Schemas: {len(invalid)}'))
            if not options['fix']:
                self.stdout.write('  Run with --fix to regenerate')
        
        if valid == total:
            self.stdout.write(self.style.SUCCESS('\n✓ All schemas valid!'))
        
        self.stdout.write('='*50)
