# Generated by Django 3.2.8 on 2022-01-16 09:23

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('suggestapp', '0003_reader_like'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reader_like',
            name='date',
            field=models.DateField(default=datetime.datetime.now),
        ),
    ]
