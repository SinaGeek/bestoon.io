# Generated by Django 4.2.2 on 2023-07-04 12:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0004_token'),
    ]

    operations = [
        migrations.RenameField(
            model_name='token',
            old_name='Token',
            new_name='token',
        ),
    ]
