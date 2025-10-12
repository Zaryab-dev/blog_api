# Generated migration for CKEditor integration

from django.db import migrations, models
import ckeditor_uploader.fields


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='content',
            field=ckeditor_uploader.fields.RichTextUploadingField(blank=True, default=''),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='post',
            name='content_html',
            field=models.TextField(editable=False),
        ),
    ]
