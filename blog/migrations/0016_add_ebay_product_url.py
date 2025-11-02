# Generated migration for eBay product URL field

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0015_add_seo_enhancements'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='ebay_product_url',
            field=models.URLField(blank=True, help_text='eBay product link', max_length=500),
        ),
    ]
