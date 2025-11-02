from django.core.management.base import BaseCommand
from django.conf import settings
from blog.models import Post


class Command(BaseCommand):
    help = 'Fix blog URLs to remove /blog/ prefix'

    def handle(self, *args, **options):
        nextjs_url = getattr(settings, 'NEXTJS_URL', 'https://zaryableather.com')
        posts = Post.objects.all()
        updated_count = 0

        for post in posts:
            updated = False

            # Fix frontend_url (remove /blog/ prefix)
            new_frontend_url = f"{nextjs_url.rstrip('/')}/{post.slug}"
            if post.frontend_url != new_frontend_url:
                post.frontend_url = new_frontend_url
                post.canonical_url = new_frontend_url
                updated = True
                self.stdout.write(f'  Old: {post.frontend_url}')
                self.stdout.write(f'  New: {new_frontend_url}')

            # Fix revalidate_path (remove /blog/ prefix)
            new_revalidate_path = f"/{post.slug}"
            if post.revalidate_path != new_revalidate_path:
                post.revalidate_path = new_revalidate_path
                updated = True

            # Fix schema_org URLs
            if post.schema_org and isinstance(post.schema_org, dict):
                schema_updated = False
                
                # Fix mainEntityOfPage
                if 'mainEntityOfPage' in post.schema_org:
                    if isinstance(post.schema_org['mainEntityOfPage'], dict):
                        old_url = post.schema_org['mainEntityOfPage'].get('@id', '')
                        if '/blog/' in old_url:
                            post.schema_org['mainEntityOfPage']['@id'] = new_frontend_url
                            schema_updated = True
                    elif isinstance(post.schema_org['mainEntityOfPage'], str):
                        if '/blog/' in post.schema_org['mainEntityOfPage']:
                            post.schema_org['mainEntityOfPage'] = new_frontend_url
                            schema_updated = True
                
                # Fix url field
                if 'url' in post.schema_org and '/blog/' in post.schema_org['url']:
                    post.schema_org['url'] = new_frontend_url
                    schema_updated = True
                
                if schema_updated:
                    updated = True

            if updated:
                post.save()
                updated_count += 1
                self.stdout.write(self.style.SUCCESS(f'✅ Updated "{post.title}"'))

        self.stdout.write(self.style.SUCCESS(
            f'\n✅ Successfully updated {updated_count} posts'
        ))
        self.stdout.write(self.style.SUCCESS(
            f'URLs now match: https://www.zaryableather.com/{"{slug}"}'
        ))
