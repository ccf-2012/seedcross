# Generated by Django 3.2.8 on 2022-04-19 04:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crseed', '0003_auto_20220207_2233'),
    ]

    operations = [
        migrations.AddField(
            model_name='processparam',
            name='cyclic_reload',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='processparam',
            name='last_load',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='processparam',
            name='max_size_difference',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='processparam',
            name='reload_interval_min',
            field=models.IntegerField(default=1440),
        ),
    ]
