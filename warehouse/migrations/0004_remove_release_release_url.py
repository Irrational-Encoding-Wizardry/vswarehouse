# Generated by Django 2.2 on 2019-04-16 09:03

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('warehouse', '0003_auto_20190416_1058'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='release',
            name='release_url',
        ),
    ]
