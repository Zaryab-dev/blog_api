# Generated migration for SEO enhancements

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0006_post_comments_count_post_likes_count_and_more'),
    ]

    operations = [
        # Add seo_keywords field to Post if not exists
        migrations.AddField(
            model_name='post',
            name='seo_keywords',
            field=models.CharField(max_length=255, blank=True, help_text='Comma-separated SEO keywords'),
        ),
        # Add og_type field
        migrations.AddField(
            model_name='post',
            name='og_type',
            field=models.CharField(max_length=20, default='article', help_text='Open Graph type'),
        ),
        # Add twitter_card field
        migrations.AddField(
            model_name='post',
            name='twitter_card',
            field=models.CharField(max_length=20, default='summary_large_image', help_text='Twitter card type'),
        ),
        # Add last_crawled field for sitemap tracking
        migrations.AddField(
            model_name='post',
            name='last_crawled',
            field=models.DateTimeField(null=True, blank=True, help_text='Last time crawled by search engines'),
        ),
        # Add priority field for sitemap
        migrations.AddField(
            model_name='post',
            name='sitemap_priority',
            field=models.DecimalField(max_digits=2, decimal_places=1, default=0.8, help_text='Sitemap priority (0.0-1.0)'),
        ),
        # Add changefreq field for sitemap
        migrations.AddField(
            model_name='post',
            name='sitemap_changefreq',
            field=models.CharField(
                max_length=10,
                default='monthly',
                choices=[
                    ('always', 'Always'),
                    ('hourly', 'Hourly'),
                    ('daily', 'Daily'),
                    ('weekly', 'Weekly'),
                    ('monthly', 'Monthly'),
                    ('yearly', 'Yearly'),
                    ('never', 'Never'),
                ],
                help_text='How frequently the page is likely to change'
            ),
        ),
    ]
