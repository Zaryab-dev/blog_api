# Generated migration for SEO enhancements

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0014_remove_comment_comment_post_idx_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='keywords',
            field=models.JSONField(blank=True, default=list, help_text='Leather-specific keywords for SEO'),
        ),
        migrations.AddField(
            model_name='post',
            name='frontend_url',
            field=models.URLField(blank=True, help_text='Public frontend URL', max_length=500),
        ),
        migrations.AddField(
            model_name='post',
            name='excerpt',
            field=models.TextField(blank=True, help_text='Short excerpt (separate from summary)', max_length=300),
        ),
        migrations.AddField(
            model_name='post',
            name='seo_score',
            field=models.IntegerField(default=0, help_text='SEO score (0-100) for Lighthouse integration'),
        ),
        migrations.AddField(
            model_name='post',
            name='structured_data_valid',
            field=models.BooleanField(default=False, help_text='Schema.org validation status'),
        ),
        migrations.AddField(
            model_name='post',
            name='main_image_alt_text',
            field=models.CharField(blank=True, help_text='Alt text for featured image', max_length=125),
        ),
        migrations.AddField(
            model_name='post',
            name='reading_time_minutes',
            field=models.IntegerField(default=0, help_text='Estimated reading time in minutes'),
        ),
        migrations.AddField(
            model_name='post',
            name='revalidate_path',
            field=models.CharField(blank=True, help_text='Path for Next.js ISR revalidation', max_length=255),
        ),
    ]
