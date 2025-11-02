from django.core.management.base import BaseCommand
from django.conf import settings
from blog.models import Post


class Command(BaseCommand):
    help = 'Update frontend URLs in canonical_url and schema_org fields'

    def handle(self, *args, **options):
        nextjs_url = getattr(settings, 'NEXTJS_URL', 'https://zaryableather.com')
        posts = Post.objects.all()
        updated_count = 0

        for post in posts:
            updated = False

            # Update frontend_url and canonical_url
            new_frontend_url = f"{nextjs_url.rstrip('/')}/{post.slug}"
            if post.frontend_url != new_frontend_url:
                post.frontend_url = new_frontend_url
                post.canonical_url = new_frontend_url
                updated = True

            # Update revalidate_path
            new_revalidate_path = f"/{post.slug}"
            if post.revalidate_path != new_revalidate_path:
                post.revalidate_path = new_revalidate_path
                updated = True

            # Update schema_org if it exists
            if post.schema_org and isinstance(post.schema_org, dict):
                # Update mainEntityOfPage
                if 'mainEntityOfPage' in post.schema_org:
                    post.schema_org['mainEntityOfPage'] = new_frontend_url
                    updated = True

                # Update publisher logo URL to use frontend domain
                if 'publisher' in post.schema_org and isinstance(post.schema_org['publisher'], dict):
                    if 'logo' in post.schema_org['publisher'] and isinstance(post.schema_org['publisher']['logo'], dict):
                        logo_url = f"{nextjs_url.rstrip('/')}/logo.png"
                        if post.schema_org['publisher']['logo'].get('url') != logo_url:
                            post.schema_org['publisher']['logo']['url'] = logo_url
                            updated = True

            if updated:
                post.save()
                updated_count += 1
                self.stdout.write(self.style.SUCCESS(f'Updated "{post.title}"'))

        self.stdout.write(self.style.SUCCESS(
            f'\nSuccessfully updated {updated_count} posts with frontend URLs'
        ))
