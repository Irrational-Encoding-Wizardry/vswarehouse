# Generated by Django 2.2 on 2019-04-15 09:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('type', models.CharField(max_length=30)),
                ('description', models.TextField()),
                ('website', models.CharField(max_length=255)),
                ('category', models.CharField(max_length=255)),
                ('identifier', models.SlugField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Release',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pypa_version', models.CharField(max_length=60)),
                ('release_version', models.CharField(max_length=60)),
                ('configuration', models.TextField()),
                ('release_url', models.URLField(max_length=100)),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='warehouse.Project')),
            ],
        ),
        migrations.CreateModel(
            name='Distribution',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pypa_platform_string', models.CharField(max_length=60)),
                ('file', models.FileField(upload_to='')),
                ('release', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='warehouse.Release')),
            ],
        ),
    ]
