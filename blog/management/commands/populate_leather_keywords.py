from django.core.management.base import BaseCommand
from blog.models import Post


class Command(BaseCommand):
    help = 'Populate leather-specific keywords for all posts'

    def handle(self, *args, **options):
        # Leather-specific keywords based on common blog topics
        leather_keywords = {
            'care': ['leather care', 'leather maintenance', 'leather cleaning', 'leather conditioning', 'leather protection'],
            'types': ['genuine leather', 'full grain leather', 'top grain leather', 'bonded leather', 'leather types'],
            'products': ['leather jacket', 'leather bag', 'leather wallet', 'leather shoes', 'leather goods'],
            'craftsmanship': ['leather craftsmanship', 'handmade leather', 'leather artisan', 'leather quality', 'leather durability'],
            'style': ['leather fashion', 'leather style', 'leather trends', 'luxury leather', 'premium leather'],
            'sustainability': ['sustainable leather', 'eco-friendly leather', 'ethical leather', 'vegan leather alternatives'],
            'buying': ['leather buying guide', 'leather shopping', 'leather investment', 'leather value'],
        }

        posts = Post.objects.all()
        updated_count = 0

        for post in posts:
            # Skip if already has keywords
            if post.keywords and len(post.keywords) > 0:
                self.stdout.write(f'Skipping "{post.title}" - already has keywords')
                continue

            # Determine relevant keywords based on title and content
            post_keywords = set()
            content_lower = (post.title + ' ' + post.summary + ' ' + post.content_html).lower()

            # Add general leather keywords
            post_keywords.update(['leather', 'leather products', 'quality leather'])

            # Add specific keywords based on content
            for category, keywords in leather_keywords.items():
                for keyword in keywords:
                    if any(word in content_lower for word in keyword.split()):
                        post_keywords.add(keyword)

            # Add category-based keywords
            for cat in post.categories.all():
                cat_name = cat.name.lower()
                if 'care' in cat_name or 'maintenance' in cat_name:
                    post_keywords.update(leather_keywords['care'][:3])
                elif 'style' in cat_name or 'fashion' in cat_name:
                    post_keywords.update(leather_keywords['style'][:3])
                elif 'guide' in cat_name or 'buying' in cat_name:
                    post_keywords.update(leather_keywords['buying'][:3])

            # Add tag-based keywords
            for tag in post.tags.all():
                tag_name = tag.name.lower()
                post_keywords.add(f'leather {tag_name}')

            # Limit to 10 keywords
            post.keywords = list(post_keywords)[:10]
            post.save(update_fields=['keywords'])
            updated_count += 1

            self.stdout.write(self.style.SUCCESS(
                f'Updated "{post.title}" with {len(post.keywords)} keywords'
            ))

        self.stdout.write(self.style.SUCCESS(
            f'\nSuccessfully updated {updated_count} posts with leather keywords'
        ))
