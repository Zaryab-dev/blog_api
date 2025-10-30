from django.contrib.postgres.operations import TrigramExtension
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0011_add_store_and_social_links'),
    ]

    operations = [
        TrigramExtension(),
    ]
