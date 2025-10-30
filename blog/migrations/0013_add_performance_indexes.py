from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0012_enable_pg_trgm'),
    ]

    operations = [
        # Add composite indexes for common queries
        migrations.AddIndex(
            model_name='post',
            index=models.Index(fields=['status', '-published_at', '-trending_score'], name='post_list_idx'),
        ),
        migrations.AddIndex(
            model_name='post',
            index=models.Index(fields=['author', 'status', '-published_at'], name='post_author_idx'),
        ),
        migrations.AddIndex(
            model_name='comment',
            index=models.Index(fields=['post', 'status', '-created_at'], name='comment_post_idx'),
        ),
        # Add indexes for foreign keys
        migrations.RunSQL(
            sql='CREATE INDEX IF NOT EXISTS post_author_id_idx ON blog_post(author_id);',
            reverse_sql='DROP INDEX IF EXISTS post_author_id_idx;',
        ),
        migrations.RunSQL(
            sql='CREATE INDEX IF NOT EXISTS post_featured_image_id_idx ON blog_post(featured_image_id);',
            reverse_sql='DROP INDEX IF EXISTS post_featured_image_id_idx;',
        ),
    ]
